#!/bin/bash
# Script to update application files in installation directory
#
# NOTE: This is an OPTIONAL automation tool for convenience.
# Experienced system administrators can manage file updates manually:
#   - Copy files using their preferred method (rsync, git, etc.)
#   - Manage backups as needed
#   - Set permissions according to their security policies
#
# Usage: ./update.sh [SOURCE_DIR] [APP_DIR] [USERNAME]
# Or set environment variables: AI_GATEWAY_SOURCE_DIR, AI_GATEWAY_APP_DIR, AI_GATEWAY_USERNAME

set -eo pipefail
IFS=$'\n\t'

# Colors
RED='\033[0;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;93m'
BLUE='\033[1;36m'
NC='\033[0m'

# Track temporary files for cleanup
TEMP_FILES=()
cleanup_temp_files() {
    local file
    for file in "${TEMP_FILES[@]}"; do
        [ -f "$file" ] && rm -f "$file" 2>/dev/null || true
    done
}
trap cleanup_temp_files EXIT INT TERM

# Function to validate path (security: prevent path traversal)
validate_path() {
    local path="$1"
    if [ -z "$path" ]; then
        return 1
    fi
    # Check for path traversal attempts
    if [[ "$path" == *".."* ]]; then
        return 1
    fi
    # Path must be absolute (start with /)
    if [[ "$path" != "/"* ]]; then
        return 1
    fi
    return 0
}

# Function to validate username (security: prevent command injection)
validate_username() {
    local username="$1"
    if [ -z "$username" ]; then
        return 1
    fi
    # Username should only contain alphanumeric, underscore, hyphen
    if [[ ! "$username" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        return 1
    fi
    return 0
}

# Get parameters
SOURCE_DIR="${1:-${AI_GATEWAY_SOURCE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}}"
APP_DIR="${2:-${AI_GATEWAY_APP_DIR:-/opt/ai-gateway}}"
USERNAME="${3:-${AI_GATEWAY_USERNAME:-aigateway}}"

# Validate paths (security)
if ! validate_path "$SOURCE_DIR"; then
    echo -e "${RED}❌ Invalid source directory path: $SOURCE_DIR${NC}" >&2
    exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ Source directory does not exist: $SOURCE_DIR${NC}" >&2
    exit 1
fi

if ! validate_path "$APP_DIR"; then
    echo -e "${RED}❌ Invalid application directory path: $APP_DIR${NC}" >&2
    exit 1
fi

if [ -z "$APP_DIR" ]; then
    echo -e "${RED}❌ Application directory cannot be empty${NC}" >&2
    exit 1
fi

# Validate username (security)
if ! validate_username "$USERNAME"; then
    echo -e "${RED}❌ Invalid username: $USERNAME${NC}" >&2
    echo -e "${YELLOW}   Username must contain only alphanumeric characters, underscore, or hyphen${NC}" >&2
    exit 1
fi

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📦 AI Gateway - Update Application Files                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Source directory:${NC} $SOURCE_DIR"
echo -e "${BLUE}Target directory:${NC} $APP_DIR"
echo -e "${BLUE}Owner:${NC} $USERNAME"
echo ""

# Check if running as root (needed for system directories)
if [ "$EUID" -ne 0 ]; then
    # Check if target directory requires root
    if [[ "$APP_DIR" == "/opt"* ]] || [[ "$APP_DIR" == "/usr"* ]] || [[ "$APP_DIR" == "/etc"* ]] || [[ "$APP_DIR" == "/var"* ]]; then
        echo -e "${YELLOW}⚠️  This script requires root privileges for system directories${NC}"
        if command -v sudo &> /dev/null; then
            echo -e "${BLUE}💡 Run with sudo:${NC}"
            echo -e "   ${GREEN}sudo $0${NC}"
            echo ""
            read -p "Run with sudo now? [Y/n]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                exec sudo -E "$0" "$SOURCE_DIR" "$APP_DIR" "$USERNAME"
            else
                echo -e "${YELLOW}Exiting.${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ sudo is not available. Please run as root.${NC}"
            exit 1
        fi
    fi
fi

# Ensure user exists
if ! id "$USERNAME" &>/dev/null; then
    echo -e "${YELLOW}⚠️  User '$USERNAME' does not exist${NC}"
    echo -e "${YELLOW}   Files will be copied but ownership may not be set correctly${NC}"
    echo ""
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ensure parent directory exists
PARENT_DIR=$(dirname "$APP_DIR")
if [ ! -d "$PARENT_DIR" ]; then
    echo -e "${BLUE}📁 Creating parent directory $PARENT_DIR...${NC}"
    mkdir -p "$PARENT_DIR"
    echo -e "${GREEN}✅ Parent directory created${NC}"
fi

# Create or prepare directory
if [ ! -d "$APP_DIR" ]; then
    echo -e "${BLUE}📁 Creating application directory $APP_DIR...${NC}"
    mkdir -p "$APP_DIR"
    if id "$USERNAME" &>/dev/null; then
        chown "$USERNAME:$USERNAME" "$APP_DIR"
    fi
    echo -e "${GREEN}✅ Directory created${NC}"
else
    # Check current owner
    if id "$USERNAME" &>/dev/null; then
        CURRENT_OWNER=$(stat -c '%U:%G' "$APP_DIR" 2>/dev/null || stat -f '%Su:%Sg' "$APP_DIR" 2>/dev/null || echo "unknown")
        if [ "$CURRENT_OWNER" != "$USERNAME:$USERNAME" ]; then
            echo -e "${YELLOW}⚠️  Current owner: $CURRENT_OWNER (will be changed to $USERNAME:$USERNAME)${NC}"
            chown "$USERNAME:$USERNAME" "$APP_DIR"
        fi
    fi
    
    # If directory is not empty, ask about backup
    if [ "$(ls -A "$APP_DIR" 2>/dev/null)" ]; then
        BACKUP_DIR="${APP_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}⚠️  Directory is not empty${NC}"
        read -p "Backup existing directory to $BACKUP_DIR? [Y/n]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            echo -e "${BLUE}📦 Creating backup to $BACKUP_DIR...${NC}"
            
            # Backup .env and config.yaml before moving directory
            ENV_BACKUP=""
            CONFIG_BACKUP=""
            if [ -f "$APP_DIR/.env" ]; then
                ENV_BACKUP=$(mktemp) || { echo -e "${RED}❌ Failed to create temporary file${NC}" >&2; exit 1; }
                TEMP_FILES+=("$ENV_BACKUP")
                cp "$APP_DIR/.env" "$ENV_BACKUP"
                echo -e "${BLUE}ℹ️  Backing up existing .env file${NC}"
            fi
            if [ -f "$APP_DIR/config.yaml" ]; then
                CONFIG_BACKUP=$(mktemp) || { echo -e "${RED}❌ Failed to create temporary file${NC}" >&2; exit 1; }
                TEMP_FILES+=("$CONFIG_BACKUP")
                cp "$APP_DIR/config.yaml" "$CONFIG_BACKUP"
                echo -e "${BLUE}ℹ️  Backing up existing config.yaml file${NC}"
            fi
            
            mv "$APP_DIR" "$BACKUP_DIR"
            mkdir -p "$APP_DIR"
            if id "$USERNAME" &>/dev/null; then
                chown "$USERNAME:$USERNAME" "$APP_DIR"
            fi
            echo -e "${GREEN}✅ Backup created, directory recreated${NC}"
            
            # Store backup directory for later restoration
            export APP_BACKUP_DIR="$BACKUP_DIR"
        fi
    fi
fi

# Copy files
if [ ! "$(ls -A "$APP_DIR" 2>/dev/null)" ] || [ ! -f "$APP_DIR/docker-compose.yml" ]; then
    echo -e "${BLUE}📦 Copying files from $SOURCE_DIR to $APP_DIR...${NC}"
else
    echo -e "${BLUE}🔄 Updating files in $APP_DIR (preserving .env and config.yaml)...${NC}"
    echo -e "${BLUE}ℹ️  This ensures you have the latest code with bug fixes${NC}"
fi

# Use tar for reliable copying with exclusions
if ! cd "$SOURCE_DIR"; then
    echo -e "${RED}❌ Cannot change to source directory: $SOURCE_DIR${NC}"
    exit 1
fi

# Backup .env and config.yaml if they exist (or restore from backup directory)
ENV_BACKUP=""
CONFIG_BACKUP=""
if [ -f "$APP_DIR/.env" ]; then
    ENV_BACKUP=$(mktemp) || { echo -e "${RED}❌ Failed to create temporary file${NC}" >&2; exit 1; }
    TEMP_FILES+=("$ENV_BACKUP")
    cp "$APP_DIR/.env" "$ENV_BACKUP"
    echo -e "${BLUE}ℹ️  Backing up existing .env file${NC}"
elif [ -n "${APP_BACKUP_DIR:-}" ] && [ -f "${APP_BACKUP_DIR}/.env" ]; then
    ENV_BACKUP=$(mktemp) || { echo -e "${RED}❌ Failed to create temporary file${NC}" >&2; exit 1; }
    TEMP_FILES+=("$ENV_BACKUP")
    cp "${APP_BACKUP_DIR}/.env" "$ENV_BACKUP"
    echo -e "${BLUE}ℹ️  Restoring .env file from backup${NC}"
fi
if [ -f "$APP_DIR/config.yaml" ]; then
    CONFIG_BACKUP=$(mktemp) || { echo -e "${RED}❌ Failed to create temporary file${NC}" >&2; exit 1; }
    TEMP_FILES+=("$CONFIG_BACKUP")
    cp "$APP_DIR/config.yaml" "$CONFIG_BACKUP"
    echo -e "${BLUE}ℹ️  Backing up existing config.yaml file${NC}"
elif [ -n "${APP_BACKUP_DIR:-}" ] && [ -f "${APP_BACKUP_DIR}/config.yaml" ]; then
    CONFIG_BACKUP=$(mktemp) || { echo -e "${RED}❌ Failed to create temporary file${NC}" >&2; exit 1; }
    TEMP_FILES+=("$CONFIG_BACKUP")
    cp "${APP_BACKUP_DIR}/config.yaml" "$CONFIG_BACKUP"
    echo -e "${BLUE}ℹ️  Restoring config.yaml file from backup${NC}"
fi

# Copy all files (excluding .git, venv, cache, and config files)
if ! tar --exclude='.git' --exclude='venv' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.env' --exclude='config.yaml' \
    -cf - . | (cd "$APP_DIR" && tar -xf -); then
    echo -e "${RED}❌ Failed to copy/update files${NC}"
    exit 1
fi

# Restore .env and config.yaml if they were backed up
if [ -n "$ENV_BACKUP" ] && [ -f "$ENV_BACKUP" ]; then
    cp "$ENV_BACKUP" "$APP_DIR/.env"
    echo -e "${GREEN}✅ Preserved existing .env file${NC}"
fi
if [ -n "$CONFIG_BACKUP" ] && [ -f "$CONFIG_BACKUP" ]; then
    cp "$CONFIG_BACKUP" "$APP_DIR/config.yaml"
    echo -e "${GREEN}✅ Preserved existing config.yaml file${NC}"
fi
# Note: Temporary files will be cleaned up by trap handler

# Clear Python cache to ensure fresh code is used
echo -e "${BLUE}🧹 Clearing Python cache...${NC}"
find "$APP_DIR" -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find "$APP_DIR" -name "*.pyc" -delete 2>/dev/null || true

# Set ownership
if id "$USERNAME" &>/dev/null; then
    echo -e "${BLUE}👤 Setting ownership to $USERNAME:$USERNAME...${NC}"
    chown -R "$USERNAME:$USERNAME" "$APP_DIR"
    echo -e "${GREEN}✅ Ownership set${NC}"
fi

# Set permissions
echo -e "${BLUE}🔐 Setting permissions...${NC}"
# Directories: 755
find "$APP_DIR" -type d -exec chmod 755 {} \;
# Scripts: 755
find "$APP_DIR" -type f -name "*.sh" -exec chmod 755 {} \;
find "$APP_DIR" -type f -name "*.bat" -exec chmod 755 {} \;
# Python scripts: 755
find "$APP_DIR" -type f -name "*.py" -exec chmod 755 {} \;
# Config files: 644
find "$APP_DIR" -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "*.txt" -o -name "*.example" \) -exec chmod 644 {} \;
# .env and config.yaml: 600
if [ -f "$APP_DIR/.env" ]; then
    chmod 600 "$APP_DIR/.env"
fi
if [ -f "$APP_DIR/config.yaml" ]; then
    chmod 600 "$APP_DIR/config.yaml"
fi
echo -e "${GREEN}✅ Permissions set${NC}"

if [ ! "$(ls -A "$APP_DIR" 2>/dev/null)" ] || [ ! -f "$APP_DIR/docker-compose.yml" ]; then
    echo -e "${GREEN}✅ Files copied${NC}"
else
    echo -e "${GREEN}✅ Files updated${NC}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Update Complete!                                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

