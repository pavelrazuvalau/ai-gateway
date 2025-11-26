#!/bin/bash
# Script to setup system user and permissions for AI Gateway
# 
# NOTE: This is an OPTIONAL automation tool for convenience.
# Experienced system administrators can perform these steps manually:
#   - Create system user with proper shell (for rootless Docker)
#   - Configure subuid/subgid mappings
#   - Set up rootless Docker
#   - Configure systemd service
#   - Set proper file permissions
#
# Run with: sudo ./user.sh

set -eo pipefail
# Note: 'set -u' is commented out to allow optional variables
# Uncomment if you want strict variable checking: set -euo pipefail
IFS=$'\n\t'

# Track temporary files for cleanup
TEMP_FILES=()
cleanup_temp_files() {
    local file
    for file in "${TEMP_FILES[@]}"; do
        [ -f "$file" ] && rm -f "$file" 2>/dev/null || true
    done
    # Also clean up docker-init-output files
    rm -f /tmp/docker-init-output.$$ 2>/dev/null || true
}
trap cleanup_temp_files EXIT INT TERM

# Function to validate paths
validate_path() {
    local path="$1"
    local path_type="${2:-file}"
    
    if [ -z "$path" ]; then
        echo "Error: Empty path provided" >&2
        return 1
    fi
    
    # Check for path traversal attempts
    if [[ "$path" == *".."* ]] || [[ "$path" == *"/"* && "$path" != "/"* ]]; then
        echo "Error: Invalid path: $path" >&2
        return 1
    fi
    
    if [ "$path_type" = "dir" ] && [ ! -d "$path" ]; then
        echo "Error: Directory does not exist: $path" >&2
        return 1
    fi
    
    return 0
}

# Function to get user home directory
get_user_home() {
    local username="$1"
    if [ -z "$username" ]; then
        echo "Error: Username required" >&2
        return 1
    fi
    getent passwd "$username" | cut -d: -f6
}

# Function to print Docker installation instructions
# Tries to use Python function, falls back to bash version
print_docker_install_instructions() {
    local username="${1:-$USERNAME}"
    
    # Try to use Python function if available
    if command -v python3 &> /dev/null && [ -f "src/platform_utils.py" ]; then
        local instructions
        instructions=$(python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from src.platform_utils import get_docker_install_instructions
    print(get_docker_install_instructions())
except Exception:
    pass
" 2>/dev/null)
        
        if [ -n "$instructions" ]; then
            echo "$instructions"
            echo ""
            echo "After installation:"
            echo "  1. Start Docker daemon:"
            echo "     sudo systemctl start docker"
            echo "     sudo systemctl enable docker"
            echo ""
            echo "  2. Add user to docker group (if using regular Docker):"
            echo "     sudo usermod -aG docker $username"
            echo ""
            echo "  3. For rootless Docker (recommended):"
            echo "     sudo -u $username dockerd-rootless-setuptool.sh install"
            echo ""
            echo "More info: https://docs.docker.com/get-docker/"
            return 0
        fi
    fi
    
    # Fallback to bash version (matches Python version)
    echo "For Ubuntu/Debian:"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo ""
    echo "For Fedora/RHEL:"
    echo "  sudo dnf install docker"
    echo ""
    echo "For Arch Linux:"
    echo "  sudo pacman -S docker"
    echo ""
    echo "After installation:"
    echo "  1. Start Docker daemon:"
    echo "     sudo systemctl start docker"
    echo "     sudo systemctl enable docker"
    echo ""
    echo "  2. Add user to docker group (if using regular Docker):"
    echo "     sudo usermod -aG docker $username"
    echo ""
    echo "  3. For rootless Docker (recommended):"
    echo "     sudo -u $username dockerd-rootless-setuptool.sh install"
    echo ""
    echo "More info: https://docs.docker.com/get-docker/"
}

# Colors
RED='\033[0;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;93m'
BLUE='\033[1;36m'
NC='\033[0m'

# Configuration variables
# Username can be overridden via environment variable
USERNAME="${AI_GATEWAY_USERNAME:-aigateway}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SYSTEMD_DIR="/etc/systemd/system"
readonly SYSTEMD_SERVICE="$SYSTEMD_DIR/ai-gateway.service"

# Function to select application directory
select_app_directory() {
    local default_dir="/opt/ai-gateway"
    local current_dir="$SOURCE_DIR"
    local selected_dir=""
    
    if [ "$EUID" -eq 0 ]; then
        # Running as root
        echo -e "${BLUE}📁 Select application installation directory:${NC}"
        echo ""
        echo -e "  1) Default: ${GREEN}$default_dir${NC} (recommended for system-wide installation)"
        echo -e "  2) Custom location"
        echo ""
        read -p "Choose option [1/2] (default: 1): " -r choice
        echo
        
        if [ -z "$choice" ] || [ "$choice" = "1" ]; then
            selected_dir="$default_dir"
        else
            while true; do
                read -p "Enter custom directory path: " -r custom_dir
                if [ -z "$custom_dir" ]; then
                    echo -e "${YELLOW}⚠️  Directory path cannot be empty${NC}"
                    continue
                fi
                # Validate path (basic check)
                if [[ "$custom_dir" == *".."* ]] || [[ "$custom_dir" != "/"* ]]; then
                    echo -e "${YELLOW}⚠️  Please enter an absolute path starting with /${NC}"
                    continue
                fi
                selected_dir="$custom_dir"
                break
            done
        fi
    else
        # Running as regular user
        echo -e "${BLUE}📁 Select application installation directory:${NC}"
        echo ""
        echo -e "  1) Current directory: ${GREEN}$current_dir${NC} (recommended for user installation)"
        echo -e "  2) Default system: ${GREEN}$default_dir${NC} (requires root)"
        echo -e "  3) Custom location"
        echo ""
        read -p "Choose option [1/2/3] (default: 1): " -r choice
        echo
        
        if [ -z "$choice" ] || [ "$choice" = "1" ]; then
            selected_dir="$current_dir"
        elif [ "$choice" = "2" ]; then
            selected_dir="$default_dir"
            echo -e "${YELLOW}⚠️  Note: Installing to $default_dir requires root privileges${NC}"
            echo -e "${YELLOW}   The script will ask for sudo when needed${NC}"
        else
            while true; do
                read -p "Enter custom directory path: " -r custom_dir
                if [ -z "$custom_dir" ]; then
                    echo -e "${YELLOW}⚠️  Directory path cannot be empty${NC}"
                    continue
                fi
                # Validate path (basic check)
                if [[ "$custom_dir" == *".."* ]] || [[ "$custom_dir" != "/"* ]]; then
                    echo -e "${YELLOW}⚠️  Please enter an absolute path starting with /${NC}"
                    continue
                fi
                selected_dir="$custom_dir"
                break
            done
        fi
    fi
    
    echo "$selected_dir"
}

# Validate critical paths
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory does not exist: $SOURCE_DIR" >&2
    exit 1
fi

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔧 AI Gateway - User & Permissions Setup                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Select application directory (before root check, so user can choose)
# If APP_DIR is set via environment variable, use it; otherwise ask user
if [ -n "${AI_GATEWAY_APP_DIR:-}" ]; then
    APP_DIR="${AI_GATEWAY_APP_DIR}"
    echo -e "${BLUE}📁 Using application directory from environment: ${GREEN}$APP_DIR${NC}"
    echo ""
else
    APP_DIR=$(select_app_directory)
    echo -e "${GREEN}✅ Selected directory: $APP_DIR${NC}"
    echo ""
fi

# Check if running as root
# Note: Some operations require root, but user installation is also possible
NEED_ROOT=false
if [ "$EUID" -ne 0 ]; then
    # Check if selected directory requires root (system directories)
    if [[ "$APP_DIR" == "/opt"* ]] || [[ "$APP_DIR" == "/usr"* ]] || [[ "$APP_DIR" == "/etc"* ]] || [[ "$APP_DIR" == "/var"* ]]; then
        NEED_ROOT=true
    fi
    
    if [ "$NEED_ROOT" = "true" ]; then
        echo -e "${YELLOW}⚠️  This script requires root privileges for system-wide installation${NC}"
        echo ""
        echo -e "${BLUE}The script needs to:${NC}"
        echo -e "  • Create system user '${USERNAME}' with full shell (required for rootless Docker)"
        echo -e "  • Add user to docker group"
        echo -e "  • Copy files to ${APP_DIR}"
        echo -e "  • Set proper ownership and permissions"
        echo -e "  • Install systemd service"
        echo ""
        if command -v sudo &> /dev/null; then
            echo -e "${BLUE}💡 Run with sudo:${NC}"
            echo -e "   ${GREEN}sudo $0${NC}"
            echo ""
            read -p "Run with sudo now? [Y/n]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                # Pass APP_DIR to sudo environment
                exec sudo -E AI_GATEWAY_APP_DIR="$APP_DIR" "$0" "$@"
            else
                echo -e "${YELLOW}Exiting. Run with sudo when ready.${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ sudo is not available. Please run as root.${NC}"
            exit 1
        fi
    else
        # User installation - root not strictly required, but some operations may need it
        echo -e "${BLUE}ℹ️  Running as regular user - some operations may require sudo${NC}"
        echo ""
    fi
fi

# 1. Create system user with full shell (required for rootless Docker)
echo -e "${BLUE}📝 Step 1: Creating system user '${USERNAME}'...${NC}"

# Check if rootless Docker is available (needed for subuid/subgid setup)
ROOTLESS_AVAILABLE=false
if command -v dockerd-rootless.sh &> /dev/null || command -v dockerd-rootless &> /dev/null; then
    ROOTLESS_AVAILABLE=true
fi

# Check if user exists and if subuid/subgid need fixing
USER_EXISTS=false
NEED_RECREATE=false
NEED_FIX_SUBUID=false

if id "$USERNAME" &>/dev/null; then
    USER_EXISTS=true
    echo -e "${GREEN}✅ User '$USERNAME' already exists${NC}"
    
    # Check if subuid/subgid are properly configured (only if rootless Docker is available)
    if [ "$ROOTLESS_AVAILABLE" = "true" ]; then
        if ! grep -q "^${USERNAME}:" /etc/subuid 2>/dev/null || ! grep -q "^${USERNAME}:" /etc/subgid 2>/dev/null; then
            echo -e "${YELLOW}⚠️  User exists but subuid/subgid are not configured${NC}"
            # Try to fix without recreating user first
            NEED_FIX_SUBUID=true
        fi
    fi
else
    # User doesn't exist, will be created
    USER_EXISTS=false
fi

# Try to fix subuid/subgid without recreating user first (professional approach)
if [ "$NEED_FIX_SUBUID" = "true" ] && [ "$USER_EXISTS" = "true" ]; then
    echo -e "${BLUE}🔧 Attempting to fix subuid/subgid without recreating user...${NC}"
    
    # Determine correct values
    CORRECT_START=100000
    CORRECT_RANGE=65536
    
    # Create backups
    SUBUID_BACKUP="/etc/subuid.backup.$(date +%Y%m%d_%H%M%S)"
    SUBGID_BACKUP="/etc/subgid.backup.$(date +%Y%m%d_%H%M%S)"
    
    FIX_SUCCEEDED=true
    if cp /etc/subuid "$SUBUID_BACKUP" 2>/dev/null && cp /etc/subgid "$SUBGID_BACKUP" 2>/dev/null; then
        # Use atomic operations
        for file in /etc/subuid /etc/subgid; do
                        temp_file=$(mktemp "${file}.tmp.XXXXXX") || { echo -e "${RED}❌ Failed to create temporary file${NC}" >&2; return 1; }
                        TEMP_FILES+=("$temp_file")
                        if cp "$file" "$temp_file" 2>/dev/null; then
                # Remove old entries
                sed -i "/^${USERNAME}:/d" "$temp_file" 2>/dev/null
                # Add correct entry
                echo "${USERNAME}:${CORRECT_START}:${CORRECT_RANGE}" >> "$temp_file"
                # Set correct permissions (users need to read for Docker)
                chmod 644 "$temp_file" 2>/dev/null || true
                # Validate (check for duplicates)
                if [ "$(grep -c "^${USERNAME}:" "$temp_file" 2>/dev/null || echo "0")" -le 1 ]; then
                    # Atomic replace
                    if mv "$temp_file" "$file" 2>/dev/null; then
                        echo -e "${GREEN}✅ Fixed ${file}${NC}"
                    else
                        rm -f "$temp_file"
                        FIX_SUCCEEDED=false
                        break
                    fi
                else
                    rm -f "$temp_file"
                    FIX_SUCCEEDED=false
                    break
                fi
            else
                rm -f "$temp_file"
                FIX_SUCCEEDED=false
                break
            fi
        done
        
        # Verify fix worked
        if [ "$FIX_SUCCEEDED" = "true" ]; then
            SUBUID_CHECK=$(grep "^${USERNAME}:" /etc/subuid 2>/dev/null)
            SUBGID_CHECK=$(grep "^${USERNAME}:" /etc/subgid 2>/dev/null)
            if [ -n "$SUBUID_CHECK" ] && [ -n "$SUBGID_CHECK" ]; then
                echo -e "${GREEN}✅ subuid/subgid fixed successfully: ${USERNAME}:${CORRECT_START}:${CORRECT_RANGE}${NC}"
                NEED_FIX_SUBUID=false
            else
                # Restore backups
                cp "$SUBUID_BACKUP" /etc/subuid 2>/dev/null
                cp "$SUBGID_BACKUP" /etc/subgid 2>/dev/null
                FIX_SUCCEEDED=false
            fi
        fi
    else
        FIX_SUCCEEDED=false
    fi
    
    # If fix failed, mark for recreation
    if [ "$FIX_SUCCEEDED" = "false" ]; then
        echo -e "${YELLOW}⚠️  Could not fix subuid/subgid automatically, will recreate user${NC}"
        NEED_RECREATE=true
    fi
fi

# Recreate user only if fix failed or user doesn't exist
if [ "$NEED_RECREATE" = "true" ]; then
    # Check if stdin is not a terminal (piped input) or AUTO_RECREATE_USER is set
    if [ ! -t 0 ] || [ "${AUTO_RECREATE_USER:-0}" = "1" ]; then
        # If input is piped (e.g., echo 'y' | script), read from stdin
        if [ ! -t 0 ]; then
            read -r RECREATE_USER || RECREATE_USER="y"
        else
            RECREATE_USER="y"
        fi
        # Auto-recreate if input was provided
        if [ "$RECREATE_USER" != "n" ] && [ "$RECREATE_USER" != "N" ]; then
            # Keep NEED_RECREATE=true
            :
        else
            NEED_RECREATE=false
        fi
    elif [ "${NON_INTERACTIVE:-0}" != "1" ]; then
        read -p "Recreate user '$USERNAME' to fix subuid/subgid configuration? [Y/n]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            NEED_RECREATE=false
        fi
    fi
    
    if [ "$NEED_RECREATE" = "true" ]; then
        echo -e "${BLUE}🗑️  Removing existing user '$USERNAME'...${NC}"
        
        # Stop any running services
        if systemctl --user -M "$USERNAME@" is-active --quiet ai-gateway 2>/dev/null; then
            echo -e "${BLUE}🛑 Stopping ai-gateway service...${NC}"
            systemctl --user -M "$USERNAME@" stop ai-gateway 2>/dev/null || true
        fi
        
        # Remove subuid/subgid entries
        if grep -q "^${USERNAME}:" /etc/subuid 2>/dev/null; then
            sed -i "/^${USERNAME}:/d" /etc/subuid
        fi
        if grep -q "^${USERNAME}:" /etc/subgid 2>/dev/null; then
            sed -i "/^${USERNAME}:/d" /etc/subgid
        fi
        
        # Remove user
        userdel -r "$USERNAME" 2>/dev/null || userdel "$USERNAME" 2>/dev/null
        echo -e "${GREEN}✅ User '$USERNAME' removed${NC}"
    fi
fi

# Create user if it doesn't exist
if ! id "$USERNAME" &>/dev/null; then
    # Use full shell (bash or sh) instead of nologin - required for rootless Docker
    # Rootless Docker needs: full HOME, XDG_RUNTIME_DIR, user-namespace, fuse, systemd-user
    USER_SHELL="/bin/bash"
    if [ ! -f "$USER_SHELL" ]; then
        USER_SHELL="/bin/sh"
    fi
    useradd -r -s "$USER_SHELL" -d "$APP_DIR" -m "$USERNAME"
    echo -e "${GREEN}✅ User '$USERNAME' created with shell $USER_SHELL${NC}"
    
    # Ensure .config directory exists for user services
    mkdir -p "$APP_DIR/.config/systemd/user"
    chown -R "$USERNAME:$USERNAME" "$APP_DIR/.config" 2>/dev/null || true
else
    # User already exists - check if shell needs to be updated for rootless Docker
    CURRENT_SHELL=$(getent passwd "$USERNAME" | cut -d: -f7)
    if [ "$CURRENT_SHELL" = "/usr/sbin/nologin" ] || [ "$CURRENT_SHELL" = "/sbin/nologin" ] || [ "$CURRENT_SHELL" = "/bin/false" ]; then
        echo -e "${YELLOW}⚠️  User '$USERNAME' exists but has nologin shell (incompatible with rootless Docker)${NC}"
        USER_SHELL="/bin/bash"
        if [ ! -f "$USER_SHELL" ]; then
            USER_SHELL="/bin/sh"
        fi
        echo -e "${BLUE}🔧 Updating shell to $USER_SHELL for rootless Docker compatibility...${NC}"
        usermod -s "$USER_SHELL" "$USERNAME"
        echo -e "${GREEN}✅ Shell updated to $USER_SHELL${NC}"
    fi
    
    # Ensure .config directory exists even if user already exists
    USER_HOME=$(get_user_home "$USERNAME")
    if [ -n "$USER_HOME" ] && [ -d "$USER_HOME" ]; then
        mkdir -p "$USER_HOME/.config/systemd/user"
        chown -R "$USERNAME:$USERNAME" "$USER_HOME/.config" 2>/dev/null || true
    fi
fi

# Configure subuid/subgid immediately after user creation (if rootless Docker is available)
# This ensures they are set up correctly before rootless Docker initialization
if [ "$ROOTLESS_AVAILABLE" = "true" ]; then
    if ! command -v newuidmap &> /dev/null || ! command -v newgidmap &> /dev/null; then
        echo -e "${BLUE}📦 Installing uidmap package (required for rootless Docker)...${NC}"
        if command -v apt &> /dev/null; then
            apt update -qq && apt install -y -qq uidmap
        elif command -v apt-get &> /dev/null; then
            apt-get update -qq && apt-get install -y -qq uidmap
        elif command -v dnf &> /dev/null; then
            dnf install -y -q shadow-utils
        elif command -v yum &> /dev/null; then
            yum install -y -q shadow-utils
        elif command -v pacman &> /dev/null; then
            pacman -S --noconfirm shadow
        else
            echo -e "${YELLOW}⚠️  Cannot auto-install uidmap. Please install it manually.${NC}"
        fi
    fi
    
    if command -v setcap &> /dev/null; then
        if [ -f /usr/bin/newuidmap ] && ! getcap cap_setuid=ep /usr/bin/newuidmap &>/dev/null; then
            setcap cap_setuid=ep /usr/bin/newuidmap 2>/dev/null || true
        fi
        if [ -f /usr/bin/newgidmap ] && ! getcap cap_setgid=ep /usr/bin/newgidmap &>/dev/null; then
            setcap cap_setgid=ep /usr/bin/newgidmap 2>/dev/null || true
        fi
    fi
    
    if ! grep -q "^${USERNAME}:" /etc/subuid 2>/dev/null || ! grep -q "^${USERNAME}:" /etc/subgid 2>/dev/null; then
        echo -e "${BLUE}🔧 Configuring subuid/subgid for user '$USERNAME'...${NC}"
        sed -i "/^${USERNAME}:/d" /etc/subuid 2>/dev/null || true
        sed -i "/^${USERNAME}:/d" /etc/subgid 2>/dev/null || true
        NEXT_SUBUID=100000
        if [ -f /etc/subuid ]; then
            MAX_END=$(awk -F: '{end=$2+$3; if(end>max) max=end} END {print max+0}' /etc/subuid 2>/dev/null)
            if [ -n "$MAX_END" ] && [ "$MAX_END" -gt 100000 ]; then
                NEXT_SUBUID=$MAX_END
            fi
        fi
        SUBUID_RANGE=65536
        echo "${USERNAME}:${NEXT_SUBUID}:${SUBUID_RANGE}" >> /etc/subuid
        echo "${USERNAME}:${NEXT_SUBUID}:${SUBUID_RANGE}" >> /etc/subgid
        chmod 644 /etc/subuid /etc/subgid 2>/dev/null || true
        echo -e "${GREEN}✅ Configured subuid/subgid: ${USERNAME}:${NEXT_SUBUID}:${SUBUID_RANGE}${NC}"
    else
        echo -e "${GREEN}✅ subuid/subgid already configured for user${NC}"
        SUBUID_ENTRY=$(grep "^${USERNAME}:" /etc/subuid)
        CURRENT_RANGE=$(echo "$SUBUID_ENTRY" | cut -d: -f3)
        if [ -n "$CURRENT_RANGE" ] && [ "$CURRENT_RANGE" -lt 65536 ]; then
            echo -e "${YELLOW}⚠️  Current subuid/subgid range (${CURRENT_RANGE}) may be too small${NC}"
            echo -e "${YELLOW}   Consider recreating user to use larger range${NC}"
        fi
    fi
fi

# 2. Setup Docker access (rootless preferred)
echo ""
echo -e "${BLUE}📝 Step 2: Setting up Docker access...${NC}"

# Check if rootless Docker is available (already checked above, but show status)
if [ "$ROOTLESS_AVAILABLE" = "true" ]; then
    echo -e "${GREEN}✅ Rootless Docker is available${NC}"
fi
if command -v dockerd-rootless.sh &> /dev/null || command -v dockerd-rootless &> /dev/null; then
    ROOTLESS_AVAILABLE=true
    echo -e "${GREEN}✅ Rootless Docker is available${NC}"
fi

# Check if regular Docker is installed
REGULAR_DOCKER=false
if command -v docker &> /dev/null; then
    REGULAR_DOCKER=true
    echo -e "${GREEN}✅ Docker is installed${NC}"
fi

if [ "$REGULAR_DOCKER" = "false" ]; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo ""
    echo -e "${YELLOW}📦 Docker Installation Instructions:${NC}"
    echo ""
    print_docker_install_instructions "$USERNAME"
    echo ""
    exit 1
fi

# Prefer rootless Docker for security
if [ "$ROOTLESS_AVAILABLE" = "true" ]; then
    echo -e "${BLUE}🔒 Setting up rootless Docker for user '$USERNAME'...${NC}"
    
    # Check if rootless Docker is already initialized for this user
    USER_HOME=$(get_user_home "$USERNAME")
    if [ -f "$USER_HOME/.docker/run/docker.sock" ] || [ -d "$USER_HOME/.local/share/docker" ]; then
        echo -e "${GREEN}✅ Rootless Docker already initialized for user${NC}"
    else
        echo -e "${BLUE}ℹ️  Rootless Docker not initialized yet${NC}"
        echo -e "${BLUE}🔧 Initializing rootless Docker for user '$USERNAME'...${NC}"
        
        # subuid/subgid should already be configured (done after user creation)
        # Just verify they exist
        if ! grep -q "^${USERNAME}:" /etc/subuid 2>/dev/null || ! grep -q "^${USERNAME}:" /etc/subgid 2>/dev/null; then
            echo -e "${RED}❌ subuid/subgid not configured for user '$USERNAME'${NC}"
            echo -e "${YELLOW}   This should have been configured during user creation${NC}"
            exit 1
        fi
        
        # Initialize rootless Docker for the user
        if command -v dockerd-rootless-setuptool.sh &> /dev/null; then
            echo -e "${BLUE}🔧 Running dockerd-rootless-setuptool.sh install...${NC}"
            echo -e "${BLUE}ℹ️  This may take a moment...${NC}"
            echo ""
            
            # Run initialization with output in real-time and capture it
            # Use timeout to prevent hanging (5 minutes should be enough)
            USER_HOME=$(get_user_home "$USERNAME")
            if [ -z "$USER_HOME" ]; then
                USER_HOME="$APP_DIR"
            fi
            
            INIT_OUTPUT=""
            # Use sudo -u with -H flag to set HOME, or runuser with explicit shell and env
            if command -v timeout &> /dev/null; then
                # Try sudo -u first (better HOME handling), fallback to runuser
                if command -v sudo &> /dev/null; then
                    if timeout 300 sudo -u "$USERNAME" -H env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                        INIT_EXIT_CODE=0
                    else
                        INIT_EXIT_CODE=$?
                    fi
                else
                    # Fallback to runuser with explicit shell
                    if timeout 300 runuser -u "$USERNAME" -s /bin/bash -- env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                        INIT_EXIT_CODE=0
                    else
                        INIT_EXIT_CODE=$?
                    fi
                fi
                TEMP_FILES+=("/tmp/docker-init-output.$$")
                INIT_OUTPUT=$(cat /tmp/docker-init-output.$$ 2>/dev/null || echo "")
            else
                # Fallback if timeout is not available
                if command -v sudo &> /dev/null; then
                    if sudo -u "$USERNAME" -H env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                        INIT_EXIT_CODE=0
                    else
                        INIT_EXIT_CODE=$?
                    fi
                else
                    # Fallback to runuser with explicit shell
                    if runuser -u "$USERNAME" -s /bin/bash -- env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                        INIT_EXIT_CODE=0
                    else
                        INIT_EXIT_CODE=$?
                    fi
                fi
                TEMP_FILES+=("/tmp/docker-init-output.$$")
                INIT_OUTPUT=$(cat /tmp/docker-init-output.$$ 2>/dev/null || echo "")
            fi
            
            echo ""
            
            # Check result
            if [ $INIT_EXIT_CODE -eq 0 ]; then
                echo -e "${GREEN}✅ Rootless Docker initialized successfully${NC}"
                
                # Check if systemd is not available (need manual setup)
                if echo "$INIT_OUTPUT" | grep -qi "systemd not detected\|systemd not found"; then
                    echo ""
                    echo -e "${YELLOW}⚠️  systemd not detected - manual Docker daemon startup required${NC}"
                    echo -e "${BLUE}🔧 Configuring environment variables automatically...${NC}"
                    
                    USER_HOME=$(get_user_home "$USERNAME")
                    if [ -z "$USER_HOME" ]; then
                        USER_HOME="$APP_DIR"
                    fi
                    
                    # Extract environment variables from output (compatible with basic grep)
                    # Try to extract from lines like: export XDG_RUNTIME_DIR=/opt/ai-gateway/.docker/run
                    XDG_RUNTIME_DIR=$(echo "$INIT_OUTPUT" | grep "export XDG_RUNTIME_DIR=" | sed -n 's/.*export XDG_RUNTIME_DIR=\([^$]*\).*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"' | tr -d "'")
                    DOCKER_HOST=$(echo "$INIT_OUTPUT" | grep "export DOCKER_HOST=" | sed -n 's/.*export DOCKER_HOST=\([^$]*\).*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"' | tr -d "'")
                    PATH_ADD=$(echo "$INIT_OUTPUT" | grep "export PATH=" | grep -v '\$PATH' | sed -n 's/.*export PATH=\([^$]*\).*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"' | tr -d "'")
                    
                    # Set defaults if not found in output
                    if [ -z "$XDG_RUNTIME_DIR" ]; then
                        XDG_RUNTIME_DIR="$USER_HOME/.docker/run"
                    fi
                    if [ -z "$DOCKER_HOST" ]; then
                        DOCKER_HOST="unix://$USER_HOME/.docker/run/docker.sock"
                    fi
                    if [ -z "$PATH_ADD" ]; then
                        PATH_ADD="/usr/bin"
                    fi
                    
                    # Add to .bashrc if it exists, otherwise .profile
                    SHELL_RC=""
                    if [ -f "$USER_HOME/.bashrc" ]; then
                        SHELL_RC="$USER_HOME/.bashrc"
                    elif [ -f "$USER_HOME/.profile" ]; then
                        SHELL_RC="$USER_HOME/.profile"
                    else
                        # Create .bashrc if it doesn't exist
                        SHELL_RC="$USER_HOME/.bashrc"
                        touch "$SHELL_RC"
                        chown "$USERNAME:$USERNAME" "$SHELL_RC"
                    fi
                    
                    # Check if already configured
                    if ! grep -q "# Docker rootless environment" "$SHELL_RC" 2>/dev/null; then
                        echo "" >> "$SHELL_RC"
                        echo "# Docker rootless environment" >> "$SHELL_RC"
                        echo "export XDG_RUNTIME_DIR=\"$XDG_RUNTIME_DIR\"" >> "$SHELL_RC"
                        echo "export PATH=\"$PATH_ADD:\$PATH\"" >> "$SHELL_RC"
                        echo "export DOCKER_HOST=\"$DOCKER_HOST\"" >> "$SHELL_RC"
                        chown "$USERNAME:$USERNAME" "$SHELL_RC"
                        echo -e "${GREEN}✅ Environment variables added to $SHELL_RC${NC}"
                    else
                        echo -e "${BLUE}ℹ️  Environment variables already configured in $SHELL_RC${NC}"
                    fi
                    
                    echo ""
                    echo -e "${YELLOW}📋 To start Docker daemon manually, run as user '$USERNAME':${NC}"
                    echo -e "${GREEN}   export XDG_RUNTIME_DIR=\"$XDG_RUNTIME_DIR\"${NC}"
                    echo -e "${GREEN}   export PATH=\"$PATH_ADD:\$PATH\"${NC}"
                    echo -e "${GREEN}   export DOCKER_HOST=\"$DOCKER_HOST\"${NC}"
                    echo -e "${GREEN}   dockerd-rootless.sh${NC}"
                    echo ""
                    echo -e "${BLUE}💡 Or use screen/tmux to run in background:${NC}"
                    echo -e "${GREEN}   screen -dmS docker dockerd-rootless.sh${NC}"
                    echo ""
                fi
            elif [ $INIT_EXIT_CODE -eq 124 ]; then
                echo -e "${RED}❌ Rootless Docker initialization timed out${NC}"
                echo -e "${YELLOW}   The process took longer than 5 minutes${NC}"
                echo -e "${YELLOW}   Please check system resources and try again${NC}"
                exit 1
            else
                echo -e "${YELLOW}⚠️  Rootless Docker initialization completed with exit code: $INIT_EXIT_CODE${NC}"
                echo -e "${YELLOW}   Check output above for details${NC}"
                
                # Check for "Missing system requirements" error
                if echo "$INIT_OUTPUT" | grep -qi "Missing system requirements"; then
                    echo ""
                    echo -e "${BLUE}🔧 Detected 'Missing system requirements' error - attempting automatic fix...${NC}"
                    
                    # Check current subuid/subgid
                    CURRENT_SUBUID=$(grep "^${USERNAME}:" /etc/subuid 2>/dev/null | head -1)
                    CURRENT_SUBGID=$(grep "^${USERNAME}:" /etc/subgid 2>/dev/null | head -1)
                    
                    # Determine correct range
                    CORRECT_START=100000
                    CORRECT_RANGE=65536
                    echo -e "${BLUE}   Using range ${CORRECT_START}:${CORRECT_RANGE}${NC}"
                    
                    # Check if fix is needed
                    NEEDS_FIX=false
                    if [ -z "$CURRENT_SUBUID" ] || [ -z "$CURRENT_SUBGID" ]; then
                        NEEDS_FIX=true
                        echo -e "${YELLOW}   Missing subuid/subgid entries${NC}"
                    else
                        CURRENT_START=$(echo "$CURRENT_SUBUID" | awk -F: '{print $2}' | tr -d '[:space:]')
                        CURRENT_RANGE=$(echo "$CURRENT_SUBUID" | awk -F: '{print $3}' | tr -d '[:space:]')
                        
                        if [ "$CURRENT_START" != "$CORRECT_START" ] || [ "$CURRENT_RANGE" != "$CORRECT_RANGE" ]; then
                            NEEDS_FIX=true
                            echo -e "${YELLOW}   Current: ${CURRENT_START}:${CURRENT_RANGE}, should be: ${CORRECT_START}:${CORRECT_RANGE}${NC}"
                        fi
                    fi
                    
                    if [ "$NEEDS_FIX" = "true" ]; then
                        echo -e "${BLUE}   Fixing subuid/subgid entries...${NC}"
                        
                        # Validate values before writing
                        if ! [[ "$CORRECT_START" =~ ^[0-9]+$ ]] || ! [[ "$CORRECT_RANGE" =~ ^[0-9]+$ ]]; then
                            echo -e "${RED}   ❌ Invalid values: start=$CORRECT_START, range=$CORRECT_RANGE${NC}"
                            return 1
                        fi
                        
                        # Create backups
                        SUBUID_BACKUP="/etc/subuid.backup.$(date +%Y%m%d_%H%M%S)"
                        SUBGID_BACKUP="/etc/subgid.backup.$(date +%Y%m%d_%H%M%S)"
                        
                        if ! cp /etc/subuid "$SUBUID_BACKUP" 2>/dev/null || ! cp /etc/subgid "$SUBGID_BACKUP" 2>/dev/null; then
                            echo -e "${RED}   ❌ Failed to create backups${NC}"
                            rm -f "$SUBUID_BACKUP" "$SUBGID_BACKUP"
                            return 1
                        fi
                        
                        # Use atomic operations with temp files
                        for file in /etc/subuid /etc/subgid; do
                            temp_file=$(mktemp "${file}.tmp.XXXXXX")
                            if ! cp "$file" "$temp_file"; then
                                echo -e "${RED}   ❌ Failed to create temp file for $file${NC}"
                                rm -f "$temp_file" "$SUBUID_BACKUP" "$SUBGID_BACKUP"
                                return 1
                            fi
                            
                            # Remove old entries
                            sed -i "/^${USERNAME}:/d" "$temp_file" 2>/dev/null
                            
                            # Add new entry
                            echo "${USERNAME}:${CORRECT_START}:${CORRECT_RANGE}" >> "$temp_file"
                            
                            # Validate temp file (check for duplicates)
                            if [ "$(grep -c "^${USERNAME}:" "$temp_file" 2>/dev/null || echo "0")" -gt 1 ]; then
                                echo -e "${RED}   ❌ Duplicate entries detected${NC}"
                                rm -f "$temp_file" "$SUBUID_BACKUP" "$SUBGID_BACKUP"
                                return 1
                            fi
                            
                            # Atomic replace
                            if ! mv "$temp_file" "$file"; then
                                echo -e "${RED}   ❌ Failed to update $file${NC}"
                                rm -f "$temp_file" "$SUBUID_BACKUP" "$SUBGID_BACKUP"
                                return 1
                            fi
                        done
                        
                        echo -e "${GREEN}✅ Fixed: ${USERNAME}:${CORRECT_START}:${CORRECT_RANGE}${NC}"
                        echo -e "${BLUE}   Backups: ${SUBUID_BACKUP}, ${SUBGID_BACKUP}${NC}"
                        echo ""
                        echo -e "${BLUE}🔄 Retrying rootless Docker initialization...${NC}"
                        
                        USER_HOME=$(get_user_home "$USERNAME")
                        if [ -z "$USER_HOME" ]; then
                            USER_HOME="$APP_DIR"
                        fi
                        
                        # Retry initialization (run as the user)
                        # Use sudo -u with -H flag for better HOME handling
                        if command -v timeout &> /dev/null; then
                            if command -v sudo &> /dev/null; then
                                if timeout 300 sudo -u "$USERNAME" -H env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            else
                                if timeout 300 runuser -u "$USERNAME" -s /bin/bash -- env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            fi
                            INIT_OUTPUT=$(cat /tmp/docker-init-output.$$ 2>/dev/null || echo "")
                            rm -f /tmp/docker-init-output.$$
                        else
                            if command -v sudo &> /dev/null; then
                                if sudo -u "$USERNAME" -H env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            else
                                if runuser -u "$USERNAME" -s /bin/bash -- env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            fi
                            INIT_OUTPUT=$(cat /tmp/docker-init-output.$$ 2>/dev/null || echo "")
                            rm -f /tmp/docker-init-output.$$
                        fi
                        
                        echo "$INIT_OUTPUT"
                        echo ""
                        
                        if [ $INIT_EXIT_CODE -eq 0 ]; then
                            echo -e "${GREEN}✅ Rootless Docker initialized successfully after fix!${NC}"
                        else
                            echo -e "${YELLOW}⚠️  Retry still failed with exit code: $INIT_EXIT_CODE${NC}"
                        fi
                    else
                        # Entries look correct but Docker still fails - check for other issues
                        echo -e "${BLUE}   subuid/subgid entries look correct: ${CURRENT_SUBUID}${NC}"
                        echo -e "${YELLOW}   Docker may be checking something else...${NC}"
                        echo ""
                        echo -e "${BLUE}🔍 Additional diagnostics:${NC}"
                        
                        # Check file permissions
                        SUBUID_PERMS=$(stat -c "%a" /etc/subuid 2>/dev/null || echo "unknown")
                        SUBGID_PERMS=$(stat -c "%a" /etc/subgid 2>/dev/null || echo "unknown")
                        echo -e "${BLUE}   /etc/subuid permissions: ${SUBUID_PERMS}${NC}"
                        echo -e "${BLUE}   /etc/subgid permissions: ${SUBGID_PERMS}${NC}"
                        
                        # Fix permissions if needed (users must be able to read)
                        if [ "$SUBUID_PERMS" != "644" ] && [ "$SUBUID_PERMS" != "0644" ]; then
                            echo -e "${YELLOW}   ⚠️  Fixing permissions on /etc/subuid and /etc/subgid...${NC}"
                            chmod 644 /etc/subuid /etc/subgid 2>/dev/null || true
                            echo -e "${GREEN}   ✅ Permissions fixed${NC}"
                        fi
                        
                        # Verify user can read files
                        if sudo -u "$USERNAME" cat /etc/subuid 2>/dev/null | grep -q "^${USERNAME}:"; then
                            echo -e "${GREEN}   ✅ User can read subuid/subgid entries${NC}"
                        else
                            echo -e "${RED}   ❌ User still cannot read entries after fix${NC}"
                        fi
                        
                        # Check if newuidmap/newgidmap are available
                        if ! command -v newuidmap &>/dev/null || ! command -v newgidmap &>/dev/null; then
                            echo -e "${YELLOW}   ⚠️  newuidmap/newgidmap not found - installing uidmap...${NC}"
                            if command -v apt &>/dev/null; then
                                apt install -y -qq uidmap 2>/dev/null || true
                            fi
                        fi
                        
                        # Check capabilities
                        if command -v getcap &>/dev/null; then
                            NEWUIDMAP_CAP=$(getcap /usr/bin/newuidmap 2>/dev/null | grep -o "cap_setuid" || echo "none")
                            NEWGIDMAP_CAP=$(getcap /usr/bin/newgidmap 2>/dev/null | grep -o "cap_setgid" || echo "none")
                            if [ "$NEWUIDMAP_CAP" != "cap_setuid" ] || [ "$NEWGIDMAP_CAP" != "cap_setgid" ]; then
                                echo -e "${YELLOW}   ⚠️  Setting capabilities for newuidmap/newgidmap...${NC}"
                                if command -v setcap &>/dev/null; then
                                    setcap cap_setuid=ep /usr/bin/newuidmap 2>/dev/null || true
                                    setcap cap_setgid=ep /usr/bin/newgidmap 2>/dev/null || true
                                fi
                            fi
                        fi
                        
                        # Try one more time after potential fixes
                        echo ""
                        echo -e "${BLUE}🔄 Retrying rootless Docker initialization after diagnostics...${NC}"
                        
                        USER_HOME=$(get_user_home "$USERNAME")
                        if [ -z "$USER_HOME" ]; then
                            USER_HOME="$APP_DIR"
                        fi
                        
                        # Use sudo -u with -H flag for better HOME handling
                        if command -v timeout &> /dev/null; then
                            if command -v sudo &> /dev/null; then
                                if timeout 300 sudo -u "$USERNAME" -H env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            else
                                if timeout 300 runuser -u "$USERNAME" -s /bin/bash -- env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            fi
                            INIT_OUTPUT=$(cat /tmp/docker-init-output.$$ 2>/dev/null || echo "")
                            rm -f /tmp/docker-init-output.$$
                        else
                            if command -v sudo &> /dev/null; then
                                if sudo -u "$USERNAME" -H env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            else
                                if runuser -u "$USERNAME" -s /bin/bash -- env HOME="$USER_HOME" dockerd-rootless-setuptool.sh install 2>&1 | tee /tmp/docker-init-output.$$; then
                                    INIT_EXIT_CODE=0
                                else
                                    INIT_EXIT_CODE=$?
                                fi
                            fi
                            INIT_OUTPUT=$(cat /tmp/docker-init-output.$$ 2>/dev/null || echo "")
                            rm -f /tmp/docker-init-output.$$
                        fi
                        
                        echo "$INIT_OUTPUT"
                        echo ""
                        
                        if [ $INIT_EXIT_CODE -eq 0 ]; then
                            echo -e "${GREEN}✅ Rootless Docker initialized successfully after diagnostics!${NC}"
                        else
                            echo -e "${YELLOW}⚠️  Still failing. This may require system-level configuration${NC}"
                        fi
                    fi
                fi
                
                # Check for "open of uid_map failed: Permission denied" error
                if echo "$INIT_OUTPUT" | grep -qi "open of uid_map failed.*Permission denied"; then
                    echo ""
                    echo -e "${RED}❌ Rootless Docker initialization failed: Cannot write to uid_map${NC}"
                    echo ""
                    echo -e "${YELLOW}⚠️  This error indicates that the user cannot create uid_map entries${NC}"
                    echo ""
                    echo -e "${BLUE}🔍 Diagnostic information:${NC}"
                    
                    # Check if user can read subuid/subgid
                    if sudo -u "$USERNAME" cat /etc/subuid 2>/dev/null | grep -q "^${USERNAME}:"; then
                        echo -e "${GREEN}   ✓ User can read subuid/subgid entries${NC}"
                    else
                        echo -e "${RED}   ❌ User cannot read subuid/subgid entries${NC}"
                        echo -e "${YELLOW}   Fixing permissions...${NC}"
                        chmod 644 /etc/subuid /etc/subgid 2>/dev/null || true
                    fi
                    
                    # Check newuidmap capabilities
                    if command -v getcap &>/dev/null; then
                        NEWUIDMAP_CAP=$(getcap /usr/bin/newuidmap 2>/dev/null | grep -o "cap_setuid" || echo "none")
                        if [ "$NEWUIDMAP_CAP" = "cap_setuid" ]; then
                            echo -e "${GREEN}   ✓ newuidmap has cap_setuid capability${NC}"
                        else
                            echo -e "${YELLOW}   ⚠️  newuidmap missing cap_setuid capability${NC}"
                            echo -e "${YELLOW}   Attempting to fix...${NC}"
                            if command -v setcap &>/dev/null; then
                                setcap cap_setuid=ep /usr/bin/newuidmap 2>/dev/null && \
                                setcap cap_setgid=ep /usr/bin/newgidmap 2>/dev/null && \
                                echo -e "${GREEN}   ✓ Fixed capabilities${NC}" || \
                                echo -e "${RED}   ❌ Failed to set capabilities${NC}"
                            fi
                        fi
                    fi
                    
                    echo ""
                    echo -e "${YELLOW}💡 This error usually means:${NC}"
                    echo -e "${YELLOW}   1. System-level configuration is required (e.g., container/VM settings)${NC}"
                    echo -e "${YELLOW}   2. User namespaces may be restricted by the kernel${NC}"
                    echo -e "${YELLOW}   3. System may need a reboot after configuration changes${NC}"
                    echo ""
                    echo -e "${BLUE}💡 Solution:${NC}"
                    echo -e "${BLUE}   • Check system documentation for enabling user namespaces${NC}"
                    echo -e "${BLUE}   • For containers/VMs, ensure proper configuration for user namespaces${NC}"
                    echo -e "${BLUE}   • Consider using a VM instead of an unprivileged container${NC}"
                    
                    echo ""
                    # Cannot use return here - we're not in a function
                    # Exit with error code instead
                    exit 1
                fi
                
                # Check for specific error patterns
                if echo "$INIT_OUTPUT" | grep -qi "Operation not permitted\|uid_map\|subuid\|subgid"; then
                    echo ""
                    echo -e "${RED}❌ Rootless Docker initialization failed due to subuid/subgid configuration issue${NC}"
                    echo ""
                    
                    # Show current entries
                    echo -e "${BLUE}📋 Current subuid/subgid entries:${NC}"
                    if grep -q "^${USERNAME}:" /etc/subuid 2>/dev/null; then
                        echo -e "${BLUE}   subuid: $(grep "^${USERNAME}:" /etc/subuid)${NC}"
                    else
                        echo -e "${YELLOW}   subuid: not found${NC}"
                    fi
                    if grep -q "^${USERNAME}:" /etc/subgid 2>/dev/null; then
                        echo -e "${BLUE}   subgid: $(grep "^${USERNAME}:" /etc/subgid)${NC}"
                    else
                        echo -e "${YELLOW}   subgid: not found${NC}"
                    fi
                    echo ""
                    
                    echo -e "${YELLOW}   Possible causes:${NC}"
                    echo -e "${YELLOW}     1. subuid/subgid entries are incorrect or conflicting${NC}"
                    echo -e "${YELLOW}     2. User needs to be recreated with proper subuid/subgid${NC}"
                    echo -e "${YELLOW}     3. System may need a reboot after subuid/subgid changes${NC}"
                    echo -e "${YELLOW}     4. Container/VM configuration may restrict user namespaces${NC}"
                    echo ""
                    echo -e "${BLUE}💡 Solution: Recreate user by running this script again and answering 'y' when asked${NC}"
                    echo ""
                    echo -e "${YELLOW}   After fixing, try: sudo -u $USERNAME dockerd-rootless-setuptool.sh install${NC}"
                fi
                
                # Check if it's already installed (exit code 1 might mean already configured)
                if runuser -u "$USERNAME" -- test -f "$USER_HOME/.docker/run/docker.sock" 2>/dev/null || \
                   runuser -u "$USERNAME" -- test -d "$USER_HOME/.local/share/docker" 2>/dev/null; then
                    echo -e "${GREEN}✅ Rootless Docker appears to be configured (socket/directory exists)${NC}"
                    INIT_EXIT_CODE=0
                elif [ $INIT_EXIT_CODE -ne 0 ]; then
                    # If initialization failed due to configuration issues, exit
                    if echo "$INIT_OUTPUT" | grep -qi "Operation not permitted\|uid_map\|subuid\|subgid"; then
                        echo ""
                        echo -e "${RED}❌ Cannot continue: Rootless Docker is required but initialization failed${NC}"
                        echo -e "${YELLOW}   Please fix the issue and run this script again${NC}"
                        exit 1
                    fi
                fi
            fi
            
            # Only continue if initialization was successful
            if [ $INIT_EXIT_CODE -eq 0 ]; then
                # Check if systemd is available
                SYSTEMD_AVAILABLE=false
                if command -v systemctl &>/dev/null && sudo -u "$USERNAME" systemctl --user list-units &>/dev/null 2>&1; then
                    SYSTEMD_AVAILABLE=true
                    # Enable lingering for user (allows user services to run without login)
                    loginctl enable-linger "$USERNAME" 2>/dev/null || true
                fi
                
                # Check if rootless Docker daemon is already running
                echo ""
                echo -e "${BLUE}🚀 Checking rootless Docker daemon status...${NC}"
                
                # Check if daemon is already running
                DOCKER_RUNNING=false
                if [ "$SYSTEMD_AVAILABLE" = "true" ]; then
                    if sudo -u "$USERNAME" systemctl --user is-active --quiet docker 2>/dev/null; then
                        DOCKER_RUNNING=true
                        echo -e "${GREEN}✅ Rootless Docker daemon is already running${NC}"
                    fi
                else
                    # Check if Docker socket exists (manual startup)
                    USER_HOME=$(get_user_home "$USERNAME")
                    [ -z "$USER_HOME" ] && USER_HOME="$APP_DIR"
                    DOCKER_SOCK="$USER_HOME/.docker/run/docker.sock"
                    if [ -S "$DOCKER_SOCK" ] 2>/dev/null; then
                        # Load environment and check
                        if [ -f "$USER_HOME/.bashrc" ]; then
                            XDG_RUNTIME_DIR=$(grep "export XDG_RUNTIME_DIR=" "$USER_HOME/.bashrc" | sed 's/.*export XDG_RUNTIME_DIR="\([^"]*\)".*/\1/' | head -1)
                            DOCKER_HOST=$(grep "export DOCKER_HOST=" "$USER_HOME/.bashrc" | sed 's/.*export DOCKER_HOST="\([^"]*\)".*/\1/' | head -1)
                        fi
                        [ -z "$XDG_RUNTIME_DIR" ] && XDG_RUNTIME_DIR="$USER_HOME/.docker/run"
                        [ -z "$DOCKER_HOST" ] && DOCKER_HOST="unix://$DOCKER_SOCK"
                        
                        if sudo -u "$USERNAME" env XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" DOCKER_HOST="$DOCKER_HOST" docker ps &>/dev/null 2>&1; then
                            DOCKER_RUNNING=true
                            echo -e "${GREEN}✅ Rootless Docker daemon is already running (manual mode)${NC}"
                        fi
                    fi
                fi
                
                if [ "$DOCKER_RUNNING" = "false" ]; then
                    # Try to start rootless Docker daemon
                    echo -e "${BLUE}   Starting rootless Docker daemon...${NC}"
                    
                    if [ "$SYSTEMD_AVAILABLE" = "true" ]; then
                        # Use systemd
                        if sudo -u "$USERNAME" -i systemctl --user start docker 2>/dev/null || \
                           sudo -u "$USERNAME" env XDG_RUNTIME_DIR="/run/user/$(id -u "$USERNAME")" systemctl --user start docker 2>/dev/null; then
                            echo -e "${GREEN}✅ Rootless Docker daemon started${NC}"
                            DOCKER_RUNNING=true
                            sleep 3
                        else
                            echo -e "${YELLOW}⚠️  Could not start rootless Docker daemon via systemd${NC}"
                            echo -e "${BLUE}ℹ️  This is normal if systemd user session is not fully initialized${NC}"
                            echo -e "${BLUE}   The daemon will start automatically when needed or can be started manually:${NC}"
                            echo -e "${GREEN}   sudo -u $USERNAME systemctl --user start docker${NC}"
                        fi
                    else
                        # Manual startup without systemd
                        USER_HOME=$(get_user_home "$USERNAME")
                        [ -z "$USER_HOME" ] && USER_HOME="$APP_DIR"
                        
                        # Load environment from .bashrc
                        XDG_RUNTIME_DIR="$USER_HOME/.docker/run"
                        DOCKER_HOST="unix://$USER_HOME/.docker/run/docker.sock"
                        PATH_ADD="/usr/bin"
                        
                        if [ -f "$USER_HOME/.bashrc" ]; then
                            XDG_RUNTIME_DIR_LOADED=$(grep "export XDG_RUNTIME_DIR=" "$USER_HOME/.bashrc" | sed 's/.*export XDG_RUNTIME_DIR="\([^"]*\)".*/\1/' | head -1)
                            DOCKER_HOST_LOADED=$(grep "export DOCKER_HOST=" "$USER_HOME/.bashrc" | sed 's/.*export DOCKER_HOST="\([^"]*\)".*/\1/' | head -1)
                            [ -n "$XDG_RUNTIME_DIR_LOADED" ] && XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR_LOADED"
                            [ -n "$DOCKER_HOST_LOADED" ] && DOCKER_HOST="$DOCKER_HOST_LOADED"
                        fi
                        
                        echo -e "${YELLOW}⚠️  systemd not available - Docker daemon needs manual startup${NC}"
                        echo -e "${BLUE}💡 To start Docker daemon manually, run as user '$USERNAME':${NC}"
                        echo -e "${GREEN}   export XDG_RUNTIME_DIR=\"$XDG_RUNTIME_DIR\"${NC}"
                        echo -e "${GREEN}   export PATH=\"$PATH_ADD:\$PATH\"${NC}"
                        echo -e "${GREEN}   export DOCKER_HOST=\"$DOCKER_HOST\"${NC}"
                        echo -e "${GREEN}   dockerd-rootless.sh${NC}"
                        echo ""
                        echo -e "${BLUE}💡 Or use screen/tmux to run in background:${NC}"
                        echo -e "${GREEN}   screen -dmS docker sudo -u $USERNAME env XDG_RUNTIME_DIR=\"$XDG_RUNTIME_DIR\" PATH=\"$PATH_ADD:\$PATH\" DOCKER_HOST=\"$DOCKER_HOST\" dockerd-rootless.sh${NC}"
                    fi
                fi
                
                # Verify Docker is accessible (if daemon is running)
                if [ "$DOCKER_RUNNING" = "true" ]; then
                    sleep 1
                    if [ "$SYSTEMD_AVAILABLE" = "true" ]; then
                        if sudo -u "$USERNAME" docker ps &>/dev/null 2>&1; then
                            echo -e "${GREEN}✅ Docker is ready and responding${NC}"
                        else
                            echo -e "${YELLOW}⚠️  Docker daemon is running but not yet ready to accept commands${NC}"
                            echo -e "${YELLOW}   It may take a few more seconds to be fully ready${NC}"
                            echo -e "${BLUE}   You can verify later with: sudo -u $USERNAME docker ps${NC}"
                        fi
                    else
                        # Manual mode - need to set environment
                        USER_HOME=$(get_user_home "$USERNAME")
                        [ -z "$USER_HOME" ] && USER_HOME="$APP_DIR"
                        XDG_RUNTIME_DIR="$USER_HOME/.docker/run"
                        DOCKER_HOST="unix://$USER_HOME/.docker/run/docker.sock"
                        
                        if [ -f "$USER_HOME/.bashrc" ]; then
                            XDG_RUNTIME_DIR_LOADED=$(grep "export XDG_RUNTIME_DIR=" "$USER_HOME/.bashrc" | sed 's/.*export XDG_RUNTIME_DIR="\([^"]*\)".*/\1/' | head -1)
                            DOCKER_HOST_LOADED=$(grep "export DOCKER_HOST=" "$USER_HOME/.bashrc" | sed 's/.*export DOCKER_HOST="\([^"]*\)".*/\1/' | head -1)
                            [ -n "$XDG_RUNTIME_DIR_LOADED" ] && XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR_LOADED"
                            [ -n "$DOCKER_HOST_LOADED" ] && DOCKER_HOST="$DOCKER_HOST_LOADED"
                        fi
                        
                        if sudo -u "$USERNAME" env XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" DOCKER_HOST="$DOCKER_HOST" docker ps &>/dev/null 2>&1; then
                            echo -e "${GREEN}✅ Docker is ready and responding${NC}"
                        else
                            echo -e "${YELLOW}⚠️  Docker daemon may need more time to start${NC}"
                            echo -e "${BLUE}   Verify with: sudo -u $USERNAME env XDG_RUNTIME_DIR=\"$XDG_RUNTIME_DIR\" DOCKER_HOST=\"$DOCKER_HOST\" docker ps${NC}"
                        fi
                    fi
                fi
            else
                echo ""
                echo -e "${YELLOW}⚠️  Rootless Docker initialization had issues${NC}"
                echo -e "${YELLOW}   You may need to run manually: sudo -u $USERNAME dockerd-rootless-setuptool.sh install${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  dockerd-rootless-setuptool.sh not found${NC}"
            echo -e "${YELLOW}   Rootless Docker will be initialized on first use${NC}"
        fi
    fi
    
    # Note: We'll use systemd user service for rootless Docker
    USE_ROOTLESS=true
else
    echo -e "${YELLOW}⚠️  Rootless Docker not available, using regular Docker${NC}"
    echo -e "${YELLOW}   For better security, consider installing rootless Docker${NC}"
    
    # Fall back to regular Docker with docker group
    if ! getent group docker > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker group does not exist. Is Docker daemon installed?${NC}"
        exit 1
    fi
    
    if groups "$USERNAME" | grep -q "\bdocker\b"; then
        echo -e "${GREEN}✅ User already in docker group${NC}"
    else
        usermod -aG docker "$USERNAME"
        echo -e "${GREEN}✅ User added to docker group${NC}"
    fi
    USE_ROOTLESS=false
fi

# 3. Create application directory and copy files
echo ""
echo -e "${BLUE}📝 Step 3: Setting up application directory...${NC}"

# Ensure user exists before creating directory
if ! id "$USERNAME" &>/dev/null; then
    echo -e "${RED}❌ User '$USERNAME' does not exist. This should not happen.${NC}"
    exit 1
fi

# Check if we need to create directory or copy files
NEED_SETUP=false
if [ "$SOURCE_DIR" = "$APP_DIR" ]; then
    # Running from /opt/ai-gateway itself - no need to copy
    echo -e "${BLUE}ℹ️  Running from $APP_DIR - using existing files${NC}"
    NEED_SETUP=false
else
    # Running from different location - need to setup
    if [ ! -d "$APP_DIR" ]; then
        echo -e "${BLUE}💡 Application directory $APP_DIR does not exist${NC}"
        echo -e "${BLUE}   We can create it with proper permissions and copy files from $SOURCE_DIR${NC}"
        echo ""
        read -p "Create directory and copy files? [Y/n]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            NEED_SETUP=true
        else
            echo -e "${YELLOW}⚠️  Skipping directory setup${NC}"
            echo -e "${YELLOW}   You can run this script again later to setup the directory${NC}"
            exit 0
        fi
    elif [ ! "$(ls -A "$APP_DIR" 2>/dev/null)" ] || [ ! -f "$APP_DIR/docker-compose.yml" ]; then
        echo -e "${BLUE}💡 Application directory $APP_DIR exists but is empty or incomplete${NC}"
        echo -e "${BLUE}   We can copy files from $SOURCE_DIR${NC}"
        echo ""
        read -p "Copy files to $APP_DIR? [Y/n]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            NEED_SETUP=true
        else
            echo -e "${YELLOW}⚠️  Skipping file copy${NC}"
            NEED_SETUP=false
        fi
    else
        echo -e "${BLUE}💡 Application directory $APP_DIR already exists and contains files${NC}"
        echo -e "${BLUE}   We can update files from $SOURCE_DIR (preserving .env and config.yaml)${NC}"
        echo ""
        read -p "Update files in $APP_DIR? [Y/n]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            NEED_SETUP=true
        else
            echo -e "${BLUE}ℹ️  Keeping existing files${NC}"
            NEED_SETUP=false
        fi
    fi
fi

# Only proceed if user confirmed
if [ "$NEED_SETUP" = "true" ]; then
    # Use dedicated update script
    UPDATE_SCRIPT="$SOURCE_DIR/update.sh"
    if [ ! -f "$UPDATE_SCRIPT" ]; then
        # If script is not in source dir, try current directory
        UPDATE_SCRIPT="$(dirname "${BASH_SOURCE[0]}")/update.sh"
    fi
    
    if [ -f "$UPDATE_SCRIPT" ]; then
        echo -e "${BLUE}📦 Using update script: $UPDATE_SCRIPT${NC}"
        echo ""
        # Run update script with proper parameters
        bash "$UPDATE_SCRIPT" "$SOURCE_DIR" "$APP_DIR" "$USERNAME"
    else
        echo -e "${YELLOW}⚠️  Update script not found at $UPDATE_SCRIPT${NC}"
        echo -e "${YELLOW}   Falling back to inline update logic${NC}"
        echo ""
        
        # Fallback to inline logic (simplified version)
        # Ensure parent directory exists
        PARENT_DIR=$(dirname "$APP_DIR")
        if [ ! -d "$PARENT_DIR" ]; then
            mkdir -p "$PARENT_DIR"
            echo -e "${BLUE}ℹ️  Created parent directory $PARENT_DIR${NC}"
        fi

        # Create directory if needed
        if [ ! -d "$APP_DIR" ]; then
            mkdir -p "$APP_DIR"
            chown "$USERNAME:$USERNAME" "$APP_DIR"
            echo -e "${GREEN}✅ Directory $APP_DIR created${NC}"
        fi

        # Copy files using tar
        echo -e "${BLUE}📦 Copying files...${NC}"
        if ! cd "$SOURCE_DIR"; then
            echo -e "${RED}❌ Cannot change to source directory: $SOURCE_DIR${NC}"
            exit 1
        fi

        # Backup config files
        ENV_BACKUP=""
        CONFIG_BACKUP=""
        [ -f "$APP_DIR/.env" ] && ENV_BACKUP=$(mktemp) && cp "$APP_DIR/.env" "$ENV_BACKUP"
        [ -f "$APP_DIR/config.yaml" ] && CONFIG_BACKUP=$(mktemp) && cp "$APP_DIR/config.yaml" "$CONFIG_BACKUP"

        # Copy files
        tar --exclude='.git' --exclude='venv' --exclude='__pycache__' \
            --exclude='*.pyc' --exclude='.env' --exclude='config.yaml' \
            -cf - . | (cd "$APP_DIR" && tar -xf -)

        # Restore config files
        [ -n "$ENV_BACKUP" ] && [ -f "$ENV_BACKUP" ] && cp "$ENV_BACKUP" "$APP_DIR/.env" && rm -f "$ENV_BACKUP"
        [ -n "$CONFIG_BACKUP" ] && [ -f "$CONFIG_BACKUP" ] && cp "$CONFIG_BACKUP" "$APP_DIR/config.yaml" && rm -f "$CONFIG_BACKUP"

        # Set ownership and permissions
        chown -R "$USERNAME:$USERNAME" "$APP_DIR"
        find "$APP_DIR" -type d -exec chmod 755 {} \;
        find "$APP_DIR" -type f -name "*.sh" -exec chmod 755 {} \;
        find "$APP_DIR" -type f -name "*.py" -exec chmod 755 {} \;
        [ -f "$APP_DIR/.env" ] && chmod 600 "$APP_DIR/.env"
        [ -f "$APP_DIR/config.yaml" ] && chmod 644 "$APP_DIR/config.yaml"
        
        echo -e "${GREEN}✅ Files updated${NC}"
    fi
fi

# 4. Set ownership
echo ""
echo -e "${BLUE}📝 Step 4: Setting ownership...${NC}"

# Verify user exists
if ! id "$USERNAME" &>/dev/null; then
    echo -e "${RED}❌ User '$USERNAME' does not exist. Cannot set ownership.${NC}"
    exit 1
fi

# Set ownership recursively
chown -R "$USERNAME:$USERNAME" "$APP_DIR"

# Verify ownership was set correctly
VERIFY_OWNER=$(stat -c '%U:%G' "$APP_DIR" 2>/dev/null || stat -f '%Su:%Sg' "$APP_DIR" 2>/dev/null || echo "unknown")
if [ "$VERIFY_OWNER" = "$USERNAME:$USERNAME" ]; then
    echo -e "${GREEN}✅ Ownership set to $USERNAME:$USERNAME (verified)${NC}"
else
    echo -e "${YELLOW}⚠️  Ownership verification: $VERIFY_OWNER (expected $USERNAME:$USERNAME)${NC}"
    echo -e "${YELLOW}   Attempting to fix...${NC}"
    chown -R "$USERNAME:$USERNAME" "$APP_DIR"
    VERIFY_OWNER2=$(stat -c '%U:%G' "$APP_DIR" 2>/dev/null || stat -f '%Su:%Sg' "$APP_DIR" 2>/dev/null || echo "unknown")
    if [ "$VERIFY_OWNER2" = "$USERNAME:$USERNAME" ]; then
        echo -e "${GREEN}✅ Ownership fixed and verified${NC}"
    else
        echo -e "${RED}❌ Failed to set ownership. Please check manually.${NC}"
        exit 1
    fi
fi

# 5. Set proper permissions
echo ""
echo -e "${BLUE}📝 Step 5: Setting permissions...${NC}"

# Directories: 755 (rwxr-xr-x)
find "$APP_DIR" -type d -exec chmod 755 {} \;

# Scripts: 755 (executable)
find "$APP_DIR" -type f -name "*.sh" -exec chmod 755 {} \;
find "$APP_DIR" -type f -name "*.bat" -exec chmod 755 {} \;

# Python scripts: 755 (executable)
find "$APP_DIR" -type f -name "*.py" -exec chmod 755 {} \;

# Config files: 644 (readable)
find "$APP_DIR" -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "*.txt" -o -name "*.example" \) -exec chmod 644 {} \;

# .env: 600 (readable/writable only by owner - contains sensitive data)
if [ -f "$APP_DIR/.env" ]; then
    chmod 600 "$APP_DIR/.env"
    echo -e "${GREEN}✅ .env set to 600 (secure)${NC}"
fi
# config.yaml: 644 (readable by owner and group - as per CHANGELOG)
if [ -f "$APP_DIR/config.yaml" ]; then
    chmod 644 "$APP_DIR/config.yaml"
    echo -e "${GREEN}✅ config.yaml set to 644${NC}"
fi

echo -e "${GREEN}✅ Permissions set${NC}"

# 6. Verify Docker access
echo ""
echo -e "${BLUE}📝 Step 6: Verifying Docker access...${NC}"

    if [ "$USE_ROOTLESS" = "true" ]; then
        # For rootless Docker, check if daemon is running
        USER_HOME=$(get_user_home "$USERNAME")
    DOCKER_SOCK="$USER_HOME/.docker/run/docker.sock"
    
    if [ -S "$DOCKER_SOCK" ]; then
        if sudo -u "$USERNAME" DOCKER_HOST="unix://$DOCKER_SOCK" docker ps &>/dev/null; then
            echo -e "${GREEN}✅ User can access rootless Docker${NC}"
        else
            echo -e "${YELLOW}⚠️  Rootless Docker socket exists but not accessible${NC}"
            echo -e "${YELLOW}   Start rootless Docker: sudo -u $USERNAME systemctl --user start docker${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Rootless Docker not initialized yet${NC}"
        echo -e "${BLUE}ℹ️  Rootless Docker will be initialized on first use${NC}"
        echo -e "${BLUE}   Or run manually: sudo -u $USERNAME dockerd-rootless-setuptool.sh install${NC}"
    fi
else
    # For regular Docker, check group access
    if sudo -u "$USERNAME" docker ps &>/dev/null; then
        echo -e "${GREEN}✅ User can access Docker${NC}"
    else
        echo -e "${YELLOW}⚠️  User cannot access Docker yet${NC}"
        echo -e "${YELLOW}   This may require restarting Docker service${NC}"
        echo -e "${YELLOW}   Or run: newgrp docker (as $USERNAME)${NC}"
    fi
fi

# 7. Setup systemd service
echo ""
echo -e "${BLUE}📝 Step 7: Setting up systemd service...${NC}"
SERVICE_FILE="$APP_DIR/ai-gateway.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${YELLOW}⚠️  Service file not found at $SERVICE_FILE${NC}"
    echo -e "${YELLOW}   Skipping systemd service installation${NC}"
else
    echo -e "${BLUE}📋 Found service file: $SERVICE_FILE${NC}"
    
    if [ "$USE_ROOTLESS" = "true" ]; then
        # For rootless Docker, use user service
        echo -e "${BLUE}🔒 Using systemd user service for rootless Docker${NC}"
        USER_HOME=$(get_user_home "$USERNAME")
        USER_SERVICE_DIR="$USER_HOME/.config/systemd/user"
        USER_SERVICE="$USER_SERVICE_DIR/ai-gateway.service"
        
        # Create user service directory
        mkdir -p "$USER_SERVICE_DIR"
        chown -R "$USERNAME:$USERNAME" "$USER_HOME/.config"
        
        # Check if service already exists
        if [ -f "$USER_SERVICE" ]; then
            echo -e "${YELLOW}⚠️  User service file already exists at $USER_SERVICE${NC}"
            read -p "Overwrite existing service file? [y/N]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${YELLOW}⚠️  Keeping existing service file${NC}"
                SKIP_SERVICE=true
            else
                SKIP_SERVICE=false
            fi
        else
            SKIP_SERVICE=false
        fi
        
        if [ "$SKIP_SERVICE" != "true" ]; then
            # Copy and modify service file for user service
            cp "$SERVICE_FILE" "$USER_SERVICE"
            chown "$USERNAME:$USERNAME" "$USER_SERVICE"
            
            # Modify service file for user service (remove User/Group, add DOCKER_HOST)
            USER_HOME=$(get_user_home "$USERNAME")
            DOCKER_SOCK="$USER_HOME/.docker/run/docker.sock"
            
            # Add DOCKER_HOST environment variable
            if ! grep -q "DOCKER_HOST" "$USER_SERVICE"; then
                # Detect sed version for compatibility (GNU vs BSD)
                if sed --version >/dev/null 2>&1; then
                    # GNU sed
                    sed -i "/^Environment=/a Environment=\"DOCKER_HOST=unix://$DOCKER_SOCK\"" "$USER_SERVICE"
                else
                    # BSD sed
                    sed -i '' "/^Environment=/a\\
Environment=\"DOCKER_HOST=unix://$DOCKER_SOCK\"" "$USER_SERVICE"
                fi
            fi
            
            # Remove User and Group lines (not needed for user service)
            if sed --version >/dev/null 2>&1; then
                # GNU sed
                sed -i '/^User=/d; /^Group=/d' "$USER_SERVICE"
            else
                # BSD sed
                sed -i '' -e '/^User=/d' -e '/^Group=/d' "$USER_SERVICE"
            fi
            
            echo -e "${GREEN}✅ User service file created at $USER_SERVICE${NC}"
            
            # Enable lingering for user (allows user services to run without login)
            loginctl enable-linger "$USERNAME" 2>/dev/null || true
            
            # Reload user systemd
            if sudo -u "$USERNAME" systemctl --user daemon-reload 2>/dev/null; then
                echo -e "${GREEN}✅ User systemd daemon reloaded${NC}"
                
                # Ask about enabling service
                echo ""
                read -p "Enable service to start on boot? [Y/n]: " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                    if sudo -u "$USERNAME" systemctl --user enable ai-gateway.service 2>/dev/null; then
                        echo -e "${GREEN}✅ User service enabled for autostart${NC}"
                    else
                        echo -e "${YELLOW}⚠️  Failed to enable user service${NC}"
                    fi
                else
                    echo -e "${BLUE}ℹ️  Service not enabled (can be enabled later with: sudo -u $USERNAME systemctl --user enable ai-gateway)${NC}"
                fi
                
                # Ask about starting service now
                echo ""
                read -p "Start service now? [Y/n]: " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                    if sudo -u "$USERNAME" systemctl --user start ai-gateway.service 2>/dev/null; then
                        echo -e "${GREEN}✅ User service started${NC}"
                        echo ""
                        echo -e "${BLUE}📊 Service status:${NC}"
                        sudo -u "$USERNAME" systemctl --user status ai-gateway.service --no-pager -l || true
                    else
                        echo -e "${YELLOW}⚠️  Failed to start service. Check logs with: sudo -u $USERNAME journalctl --user -u ai-gateway${NC}"
                    fi
                else
                    echo -e "${BLUE}ℹ️  Service not started (can be started later with: sudo -u $USERNAME systemctl --user start ai-gateway)${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  Failed to reload user systemd daemon${NC}"
                echo -e "${YELLOW}   Service file copied but not activated${NC}"
            fi
        fi
    else
        # For regular Docker, use system service
        echo -e "${BLUE}📋 Using systemd system service${NC}"
        
        # Check if service already exists
        if [ -f "$SYSTEMD_SERVICE" ]; then
            echo -e "${YELLOW}⚠️  Service file already exists at $SYSTEMD_SERVICE${NC}"
            read -p "Overwrite existing service file? [y/N]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${YELLOW}⚠️  Keeping existing service file${NC}"
                SKIP_SERVICE=true
            else
                SKIP_SERVICE=false
            fi
        else
            SKIP_SERVICE=false
        fi
        
        if [ "$SKIP_SERVICE" != "true" ]; then
            # Copy service file
            cp "$SERVICE_FILE" "$SYSTEMD_SERVICE"
            echo -e "${GREEN}✅ Service file copied to $SYSTEMD_SERVICE${NC}"
            
            # Reload systemd
            if systemctl daemon-reload 2>/dev/null; then
                echo -e "${GREEN}✅ Systemd daemon reloaded${NC}"
                
                # Ask about enabling service
                echo ""
                read -p "Enable service to start on boot? [Y/n]: " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                    if systemctl enable ai-gateway.service 2>/dev/null; then
                        echo -e "${GREEN}✅ Service enabled for autostart${NC}"
                    else
                        echo -e "${YELLOW}⚠️  Failed to enable service${NC}"
                    fi
                else
                    echo -e "${BLUE}ℹ️  Service not enabled (can be enabled later with: systemctl enable ai-gateway)${NC}"
                fi
                
                # Ask about starting service now
                echo ""
                read -p "Start service now? [Y/n]: " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                    if systemctl start ai-gateway.service 2>/dev/null; then
                        echo -e "${GREEN}✅ Service started${NC}"
                        echo ""
                        echo -e "${BLUE}📊 Service status:${NC}"
                        systemctl status ai-gateway.service --no-pager -l || true
                    else
                        echo -e "${YELLOW}⚠️  Failed to start service. Check logs with: journalctl -u ai-gateway${NC}"
                    fi
                else
                    echo -e "${BLUE}ℹ️  Service not started (can be started later with: systemctl start ai-gateway)${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  Failed to reload systemd daemon${NC}"
                echo -e "${YELLOW}   Service file copied but not activated${NC}"
                echo -e "${YELLOW}   Run manually: systemctl daemon-reload${NC}"
            fi
        fi
    fi
fi

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Setup Complete!                                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "   User: ${GREEN}$USERNAME${NC}"
echo -e "   Home/App Directory: ${GREEN}$APP_DIR${NC}"
echo -e "   Groups: ${GREEN}$(groups $USERNAME | cut -d: -f2 | xargs)${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
if [ "$USE_ROOTLESS" = "true" ]; then
    USER_HOME=$(get_user_home "$USERNAME")
    USER_SERVICE_DIR="$USER_HOME/.config/systemd/user"
    USER_SERVICE="$USER_SERVICE_DIR/ai-gateway.service"
    
    if [ -f "$USER_SERVICE" ]; then
        ACTUAL_SERVICE="$USER_SERVICE"
        echo -e "   1. Run initial setup: ${GREEN}sudo -u $USERNAME $APP_DIR/setup.sh${NC}"
        echo -e "   2. User service is installed at: ${GREEN}$ACTUAL_SERVICE${NC}"
        echo -e "   3. Manage service: ${GREEN}sudo -u $USERNAME systemctl --user {start|stop|restart|status} ai-gateway${NC}"
        echo -e "   4. View logs: ${GREEN}sudo -u $USERNAME journalctl --user -u ai-gateway -f${NC}"
        echo -e "   5. Rootless Docker socket: ${GREEN}$USER_HOME/.docker/run/docker.sock${NC}"
    else
        echo -e "   1. Initialize rootless Docker: ${GREEN}sudo -u $USERNAME dockerd-rootless-setuptool.sh install${NC}"
        echo -e "   2. Run initial setup: ${GREEN}sudo -u $USERNAME $APP_DIR/setup.sh${NC}"
        echo -e "   3. Start service manually: ${GREEN}sudo -u $USERNAME $APP_DIR/start.sh${NC}"
    fi
elif [ -f "$SYSTEMD_SERVICE" ]; then
    echo -e "   1. Run initial setup: ${GREEN}sudo -u $USERNAME $APP_DIR/setup.sh${NC}"
    echo -e "   2. Service is installed at: ${GREEN}$SYSTEMD_SERVICE${NC}"
    echo -e "   3. Manage service: ${GREEN}sudo systemctl {start|stop|restart|status} ai-gateway${NC}"
    echo -e "   4. View logs: ${GREEN}sudo journalctl -u ai-gateway -f${NC}"
else
    echo -e "   1. Switch to user: ${GREEN}sudo -u $USERNAME -s${NC}"
    echo -e "   2. Or run commands as: ${GREEN}sudo -u $USERNAME <command>${NC}"
    echo -e "   3. Navigate to: ${GREEN}cd $APP_DIR${NC}"
    echo -e "   4. Run setup: ${GREEN}sudo -u $USERNAME $APP_DIR/setup.sh${NC}"
    echo -e "   5. Start service: ${GREEN}sudo -u $USERNAME $APP_DIR/start.sh${NC}"
fi
echo ""
echo -e "${YELLOW}💡 Notes:${NC}"
if [ "$USE_ROOTLESS" = "true" ]; then
    echo -e "   • Using rootless Docker for enhanced security 🔒${NC}"
    echo -e "   • Rootless Docker daemon runs as user $USERNAME${NC}"
    USER_HOME=$(get_user_home "$USERNAME")
    USER_SERVICE_DIR="$USER_HOME/.config/systemd/user"
    USER_SERVICE="$USER_SERVICE_DIR/ai-gateway.service"
    if [ -f "$USER_SERVICE" ]; then
        echo -e "   • User service will start automatically on boot (if enabled)${NC}"
    fi
    echo -e "   • Start rootless Docker: ${GREEN}sudo -u $USERNAME systemctl --user start docker${NC}"
elif [ -f "$SYSTEMD_SERVICE" ]; then
    echo -e "   • Service will start automatically on boot (if enabled)${NC}"
    echo -e "   • If Docker access doesn't work: ${GREEN}sudo systemctl restart docker${NC}"
    echo -e "   • Or log out/in to refresh group membership${NC}"
else
    if [ "$USE_ROOTLESS" != "true" ]; then
        echo -e "   • If Docker access doesn't work: ${GREEN}sudo systemctl restart docker${NC}"
        echo -e "   • Or log out/in to refresh group membership${NC}"
    fi
fi
echo ""

