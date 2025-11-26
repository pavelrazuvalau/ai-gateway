#!/bin/bash
# Startup script with configuration check

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Define colors early
# Use regular variables (not readonly) to allow script_init.sh to override if needed
RED='\033[0;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;93m'
BLUE='\033[1;36m'
NC='\033[0m'

# Block execution as root - must run as regular user
if [ "$(id -u)" -eq 0 ]; then
    echo -e "${RED}❌ This script must not be run as root${NC}"
    echo ""
    echo -e "${YELLOW}This script is designed to run as a regular user.${NC}"
    echo -e "${YELLOW}It will work from the current directory where you run it.${NC}"
    echo ""
    echo -e "${BLUE}💡 To run as a different user:${NC}"
    echo -e "${GREEN}   sudo -u username ./start.sh${NC}"
    echo ""
    echo -e "${BLUE}💡 Or switch to the user first:${NC}"
    echo -e "${GREEN}   su - username${NC}"
    echo -e "${GREEN}   ./start.sh${NC}"
    echo ""
    exit 1
fi

# Function to ensure and activate virtual environment
# Returns 0 on success, 1 on failure
ensure_venv() {
    local venv_dir="$SCRIPT_DIR/venv"
    local venv_activate="$venv_dir/bin/activate"
    
    # If venv exists and is valid, activate it
    if [ -d "$venv_dir" ] && [ -f "$venv_activate" ]; then
        # shellcheck source=/dev/null
        source "$venv_activate"
        return 0
    fi
    
    # Virtual environment doesn't exist, create it
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo -e "${BLUE}Creating virtual environment...${NC}"
    
    # Use venv.sh if available, otherwise create directly
    if [ -f "$SCRIPT_DIR/venv.sh" ]; then
        if ! "$SCRIPT_DIR/venv.sh"; then
            return 1
        fi
    else
        # Direct creation
        if ! python3 -m venv "$venv_dir" 2>&1; then
            echo ""
            echo -e "${YELLOW}⚠️  The virtual environment was not created because ensurepip is not available.${NC}"
            echo ""
            echo -e "${BLUE}On Debian/Ubuntu systems, install the python3-venv package:${NC}"
            echo -e "${GREEN}  sudo apt install python3-venv${NC}"
            echo ""
            echo -e "${RED}❌ Failed to create virtual environment${NC}"
            return 1
        fi
        
        # Activate and install dependencies
        # shellcheck source=/dev/null
        source "$venv_activate"
        pip install --quiet --upgrade pip setuptools wheel 2>/dev/null || true
        if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
            pip install --quiet -r "$SCRIPT_DIR/requirements.txt" || return 1
        fi
    fi
    
    # Verify activation
    if [ ! -f "$venv_activate" ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        return 1
    fi
    
    # shellcheck source=/dev/null
    source "$venv_activate"
    return 0
}

# Note: Script now runs only as regular user from current directory
# No automatic file copying or user creation

# Non-interactive mode support
if [ "${NON_INTERACTIVE:-0}" = "1" ]; then
    AUTO_YES="y"
else
    AUTO_YES=""
fi

# Load common initialization module
if [ -f "src/script_init.sh" ]; then
    source src/script_init.sh
fi

# Run dependency checks using unified function
# Note: We don't exit on Docker daemon errors - bash check_docker() will handle it
if ! init_script_with_checks "start" "Starting AI Gateway" "🚀"; then
    # Check if it's just Docker daemon issue (non-critical for start.sh)
    # We'll let bash check_docker() handle Docker daemon startup
    if command -v docker &>/dev/null && docker --version &>/dev/null && ! docker ps &>/dev/null 2>&1; then
        # Docker is installed but daemon is not running - this is OK, will be handled below
        echo ""
        echo -e "${BLUE}ℹ️  Docker daemon is not running - will be handled below...${NC}"
        echo ""
    else
        # Other critical errors (missing Docker, etc.)
        # Note: Missing .env is handled below with interactive prompt
        # If .env exists, continue - Docker daemon check will be done below
        if [ -f ".env" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  Some dependency checks failed, but continuing...${NC}"
            echo ""
        else
            # If .env doesn't exist, exit - script will prompt for setup
            exit 1
        fi
    fi
fi

# Check for .env file (only if running from /opt/ai-gateway)
# Note: If running from wrong directory, we already exited above
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo ""
    echo -e "${YELLOW}Environment needs to be configured first.${NC}"
    echo ""
    
    if [ -n "$AUTO_YES" ]; then
        REPLY="y"
        echo -e "${BLUE}Non-interactive mode: auto-confirming${NC}"
    else
        read -p "Run setup to configure? [Y/n]: " -n 1 -r
    fi
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo ""
        echo -e "${BLUE}Running setup...${NC}"
        echo ""
        
        # Check and activate venv
        if ! ensure_venv; then
            exit 1
        fi
        
        # Run setup
        if ! "$SCRIPT_DIR/ai-gateway" setup; then
            echo ""
            echo -e "${RED}❌ Setup failed${NC}"
            exit 1
        fi
        
        # Verify .env was created
        if [ ! -f ".env" ]; then
            echo ""
            echo -e "${RED}❌ Setup completed but .env file was not created${NC}"
            exit 1
        fi
        
        echo ""
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo ""
        echo -e "${BLUE}💡 Starting containers automatically...${NC}"
        echo ""
        
        # Continue with container startup (don't exit)
        # The script will continue below to start containers
    else
        echo -e "${YELLOW}Setup cancelled. Create .env file manually or run ./setup.sh.${NC}"
        exit 1
    fi
fi

# Check .env configuration
echo -e "${BLUE}🔍 Checking .env configuration...${NC}"

# Check master key
if ! grep -q "^LITELLM_MASTER_KEY=" .env || grep -q "^LITELLM_MASTER_KEY=$" .env; then
    echo -e "${RED}❌ LITELLM_MASTER_KEY not configured in .env${NC}"
    echo ""
    echo -e "${YELLOW}The .env file needs to be configured.${NC}"
    if [ -n "$AUTO_YES" ]; then
        REPLY="y"
        echo -e "${BLUE}Non-interactive mode: auto-confirming${NC}"
    else
        read -p "Run setup to configure? [Y/n]: " -n 1 -r
    fi
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Check and activate venv
        if ! ensure_venv; then
            exit 1
        fi
        "$SCRIPT_DIR/ai-gateway" setup
        exit 0
    else
        exit 1
    fi
fi

# API keys are configured via Admin UI, no check required
echo -e "${GREEN}✅ .env file configured${NC}"
echo -e "${BLUE}💡 Providers, API keys and models are configured through LiteLLM Admin UI${NC}"
echo ""

# Check Docker (function from script_init.sh will offer to start it)
# This check is done AFTER Python checks to ensure interactive Docker setup
echo ""
echo -e "${BLUE}🔍 Checking Docker daemon...${NC}"

# Ensure check_docker function is available
if ! type check_docker &>/dev/null; then
    echo -e "${YELLOW}⚠️  check_docker function not found, loading script_init.sh...${NC}"
    if [ -f "src/script_init.sh" ]; then
        source src/script_init.sh
    else
        echo -e "${RED}❌ Cannot find script_init.sh${NC}"
        exit 1
    fi
fi

# Function to print Docker daemon start instructions
print_docker_start_instructions() {
    # Detect platform
    local platform
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        platform="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        platform="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        platform="windows"
    else
        platform="unknown"
    fi
    
    echo -e "${BLUE}ℹ️  To start Docker daemon:${NC}"
    echo ""
    
    if [ "$platform" = "linux" ]; then
        echo -e "${BLUE}For rootless Docker (recommended, more secure):${NC}"
        echo "  1. If rootless Docker is not initialized:"
        echo "     dockerd-rootless-setuptool.sh install"
        echo "     # This will initialize and automatically start the daemon"
        echo ""
        echo "  2. If rootless Docker is already initialized but daemon is not running:"
        echo "     systemctl --user start docker"
        echo "     systemctl --user enable docker  # Enable auto-start on login"
        echo ""
        echo -e "${BLUE}For system-wide Docker (requires sudo):${NC}"
        echo "  sudo systemctl start docker"
        echo "  sudo systemctl enable docker  # Enable auto-start on boot"
    elif [ "$platform" = "macos" ]; then
        echo "  Start Docker Desktop from Applications"
        echo "  Or via command line:"
        echo "    open -a Docker"
    elif [ "$platform" = "windows" ]; then
        echo "  Start Docker Desktop from Start menu"
        echo "  Or check that Docker Desktop is running in system tray"
        echo ""
        echo "  If using WSL2:"
        echo "    wsl"
        echo "    sudo service docker start"
    else
        echo "  Please start Docker daemon for your platform"
    fi
    
    echo ""
    echo -e "${BLUE}ℹ️  After starting Docker, run this script again:${NC}"
    echo -e "${GREEN}   ./start.sh${NC}"
    echo ""
}

if ! check_docker; then
    echo ""
    echo -e "${RED}❌ Docker daemon is not running and could not be started${NC}"
    echo ""
    print_docker_start_instructions
    exit 1
fi

# Verify Docker is actually working
if ! docker ps &> /dev/null; then
    echo ""
    echo -e "${RED}❌ Docker daemon is not responding${NC}"
    echo ""
    print_docker_start_instructions
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready${NC}"
echo ""

# Check and synchronize PostgreSQL password
echo -e "${BLUE}🔍 Checking PostgreSQL configuration...${NC}"

# Load variables from .env (safely)
# Use set -a to export all variables, then source .env
if [ -f ".env" ]; then
    set -a
    # shellcheck source=/dev/null
    source .env
    set +a
fi

# Check and select budget profile
if [ -z "$BUDGET_PROFILE" ]; then
    BUDGET_PROFILE="test"  # Default to test
fi

# Can be overridden via command line argument
NEED_REGEN_CONFIG=false
if [ $# -gt 0 ]; then
    if [ "$1" = "prod" ] || [ "$1" = "production" ]; then
        BUDGET_PROFILE="prod"
        NEED_REGEN_CONFIG=true
        echo -e "${BLUE}📊 Using budget profile: ${GREEN}prod${NC}"
    elif [ "$1" = "test" ]; then
        BUDGET_PROFILE="test"
        NEED_REGEN_CONFIG=true
        echo -e "${BLUE}📊 Using budget profile: ${YELLOW}test${NC}"
    elif [ "$1" = "unlimited" ]; then
        BUDGET_PROFILE="unlimited"
        NEED_REGEN_CONFIG=true
        echo -e "${BLUE}📊 Using budget profile: ${YELLOW}unlimited${NC}"
    else
        if [ -n "$BUDGET_PROFILE" ]; then
            echo -e "${BLUE}📊 Budget profile from .env: ${GREEN}${BUDGET_PROFILE}${NC}"
        fi
    fi
else
    if [ -n "$BUDGET_PROFILE" ]; then
        echo -e "${BLUE}📊 Budget profile from .env: ${GREEN}${BUDGET_PROFILE}${NC}"
    fi
fi

export BUDGET_PROFILE

# Regenerate config.yaml if profile specified via argument
if [ "$NEED_REGEN_CONFIG" = "true" ] && [ -f "config.yaml" ] && command -v python3 &> /dev/null; then
    echo -e "${BLUE}🔄 Regenerating config.yaml with profile: ${GREEN}${BUDGET_PROFILE}${NC}"
    # Simply run setup.py in quick_mode to regenerate config.yaml
    # But this requires interactive input... Better just warn
    echo -e "${YELLOW}⚠️  To apply new budget profile run: ${GREEN}./setup.sh${NC}"
    echo -e "${YELLOW}   Or manually update max_budget in config.yaml${NC}"
    echo ""
fi

# Check if PostgreSQL volume exists
POSTGRES_VOLUME="ai-gateway_postgres_data"
if docker volume ls | grep -q "$POSTGRES_VOLUME"; then
    # Volume exists - check if PostgreSQL can connect with current password
    echo -e "${BLUE}ℹ️  PostgreSQL volume exists${NC}"
    
    # Check if PostgreSQL is running
    if docker ps | grep -q "litellm-postgres"; then
        # Try to connect with password from .env
        if ! docker exec litellm-postgres psql -U "${POSTGRES_USER:-litellm}" -d "${POSTGRES_DB:-litellm}" -c "SELECT 1;" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  PostgreSQL cannot connect with current password${NC}"
            echo -e "${YELLOW}   Password might have been changed in .env${NC}"
            echo ""
            if [ -n "$AUTO_YES" ]; then
                REPLY="y"
                echo -e "${BLUE}Non-interactive mode: auto-confirming${NC}"
            else
                read -p "Recreate PostgreSQL volume with new password? [Y/n]: " -n 1 -r
            fi
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                echo -e "${BLUE}🛑 Stopping containers...${NC}"
                docker compose stop postgres litellm 2>/dev/null || true
                
                echo -e "${BLUE}🗑️  Removing PostgreSQL volume...${NC}"
                docker volume rm "$POSTGRES_VOLUME" 2>/dev/null || true
                
                echo -e "${GREEN}✅ PostgreSQL volume will be recreated with new password${NC}"
            else
                echo -e "${YELLOW}⚠️  Continuing with current password (connection error may occur)${NC}"
            fi
        else
            echo -e "${GREEN}✅ PostgreSQL uses correct password${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  PostgreSQL is not running, will be created on startup${NC}"
    fi
else
    echo -e "${BLUE}ℹ️  PostgreSQL volume does not exist, will be created on first startup${NC}"
fi

echo ""

# Start containers using Python module (waits for health checks)
echo -e "${BLUE}🚀 Starting containers...${NC}"
echo ""

# Use ai-gateway CLI to start containers (uses StartService with health check waiting)
if ! "$SCRIPT_DIR/ai-gateway" start; then
    echo ""
    echo -e "${RED}❌ Failed to start containers${NC}"
    echo -e "${YELLOW}   Check logs: docker compose logs${NC}"
    exit 1
fi
