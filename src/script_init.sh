#!/bin/bash
# Common initialization module for bash scripts
# Usage: source src/script_init.sh

# Colors (consistent for all scripts)
# Only set if not already set (to avoid readonly conflicts)
: "${RED:='\033[0;31m'}"
: "${GREEN:='\033[1;32m'}"
: "${YELLOW:='\033[1;93m'}"
: "${BLUE:='\033[1;36m'}"
: "${CYAN:='\033[0;36m'}"
: "${NC:='\033[0m'}"

# Function to print banner
print_banner() {
    local emoji="$1"
    local title="$2"
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  ${emoji} ${title:<47}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to check and start Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        return 1
    fi
    
    local version
    version=$(docker --version 2>/dev/null | head -n1 || echo "Docker")
    
    if ! docker ps &> /dev/null; then
        echo -e "${YELLOW}⚠️  Docker daemon is not running${NC}"
        echo ""
        
        # Check if rootless Docker is available
        local ROOTLESS_AVAILABLE=false
        if command -v dockerd-rootless.sh &> /dev/null || command -v dockerd-rootless &> /dev/null; then
            ROOTLESS_AVAILABLE=true
        fi
        
        # Check if rootless Docker is initialized for current user
        local ROOTLESS_INITIALIZED=false
        local USER_HOME="${HOME:-$(getent passwd "$USER" 2>/dev/null | cut -d: -f6)}"
        if [ -z "$USER_HOME" ]; then
            USER_HOME="$HOME"
        fi
        
        # Check multiple indicators of rootless Docker initialization
        if [ -f "$USER_HOME/.docker/run/docker.sock" ] || \
           [ -d "$USER_HOME/.local/share/docker" ] || \
           [ -d "$USER_HOME/.config/systemd/user" ] || \
           systemctl --user list-unit-files docker.service &>/dev/null; then
            ROOTLESS_INITIALIZED=true
        fi
        
        # Check if rootless Docker service is running
        local ROOTLESS_RUNNING=false
        if [ "$ROOTLESS_INITIALIZED" = "true" ]; then
            if systemctl --user is-active --quiet docker 2>/dev/null; then
                ROOTLESS_RUNNING=true
            fi
        fi
        
        # Determine Docker mode
        if [ "$ROOTLESS_AVAILABLE" = "true" ]; then
            if [ "$ROOTLESS_INITIALIZED" = "false" ]; then
                # Rootless Docker available but not initialized
                echo -e "${BLUE}💡 Rootless Docker is available but not initialized for user '$USER'${NC}"
                echo ""
                # Ask user interactively (unless in non-interactive mode)
                if [ "${NON_INTERACTIVE:-0}" = "1" ]; then
                    AUTO_INIT="n"
                    echo -e "${YELLOW}⚠️  Non-interactive mode: skipping rootless Docker initialization${NC}"
                    echo -e "${YELLOW}   Run manually: dockerd-rootless-setuptool.sh install${NC}"
                else
                    # Always show interactive prompt - rootless Docker initialization requires proper setup
                    read -p "Initialize and start rootless Docker now? [Y/n]: " -n 1 -r
                    echo
                    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                        AUTO_INIT="y"
                    else
                        AUTO_INIT="n"
                    fi
                fi
                
                if [ "$AUTO_INIT" = "y" ]; then
                    echo ""
                    echo -e "${BLUE}🔧 Initializing rootless Docker...${NC}"
                    
                    # Check if uidmap is installed
                    if ! command -v newuidmap &> /dev/null || ! command -v newgidmap &> /dev/null; then
                        echo -e "${RED}❌ uidmap package is not installed${NC}"
                        echo -e "${YELLOW}   Rootless Docker requires uidmap package${NC}"
                        echo -e "${YELLOW}   Install it with:${NC}"
                        echo -e "${YELLOW}     Ubuntu/Debian: sudo apt install uidmap${NC}"
                        echo -e "${YELLOW}     Fedora/RHEL: sudo dnf install shadow-utils${NC}"
                        echo -e "${YELLOW}     Arch: sudo pacman -S shadow${NC}"
                        echo -e "${YELLOW}   Or run: sudo ./user.sh${NC}"
                        return 1
                    fi
                    
                    # Check if subuid/subgid are configured
                    if ! grep -q "^${USER}:" /etc/subuid 2>/dev/null; then
                        echo -e "${RED}❌ subuid not configured for user '$USER'${NC}"
                        echo -e "${YELLOW}   Rootless Docker requires subuid/subgid configuration${NC}"
                        echo -e "${YELLOW}   Run as root to configure:${NC}"
                        echo -e "${YELLOW}     sudo ./setup_user.sh${NC}"
                        echo -e "${YELLOW}   Or manually add to /etc/subuid:${NC}"
                        echo -e "${YELLOW}     ${USER}:100000:65536${NC}"
                        return 1
                    fi
                    
                    if ! grep -q "^${USER}:" /etc/subgid 2>/dev/null; then
                        echo -e "${RED}❌ subgid not configured for user '$USER'${NC}"
                        echo -e "${YELLOW}   Rootless Docker requires subuid/subgid configuration${NC}"
                        echo -e "${YELLOW}   Run as root to configure:${NC}"
                        echo -e "${YELLOW}     sudo ./setup_user.sh${NC}"
                        echo -e "${YELLOW}   Or manually add to /etc/subgid:${NC}"
                        echo -e "${YELLOW}     ${USER}:100000:65536${NC}"
                        return 1
                    fi
                    
                    if command -v dockerd-rootless-setuptool.sh &> /dev/null; then
                        # Run initialization and capture output
                        INIT_OUTPUT=$(dockerd-rootless-setuptool.sh install 2>&1)
                        INIT_EXIT_CODE=$?
                        echo "$INIT_OUTPUT"
                        
                        # Check for "Operation not permitted" error
                        if echo "$INIT_OUTPUT" | grep -qi "Operation not permitted\|uid_map\|subuid\|subgid"; then
                            echo ""
                            echo -e "${RED}❌ Rootless Docker initialization failed: Operation not permitted${NC}"
                            echo ""
                            echo -e "${YELLOW}   This usually means subuid/subgid are not properly configured${NC}"
                            echo -e "${YELLOW}   Or system-level configuration is required (e.g., container/VM settings)${NC}"
                            echo ""
                            echo -e "${BLUE}💡 Solution:${NC}"
                            echo -e "${BLUE}   Run as root: sudo ./user.sh${NC}"
                            echo -e "${BLUE}   For containers/VMs, ensure proper configuration for user namespaces${NC}"
                            echo -e "${BLUE}   Consider using a VM instead of an unprivileged container${NC}"
                            echo ""
                            return 1
                        fi
                        
                        # Check if initialization was successful
                        if [ $INIT_EXIT_CODE -eq 0 ] || echo "$INIT_OUTPUT" | grep -q "already installed\|already configured\|installed successfully"; then
                            echo -e "${GREEN}✅ Rootless Docker initialized${NC}"
                            
                            # Check if systemd is not available
                            if echo "$INIT_OUTPUT" | grep -qi "systemd not detected\|systemd not found"; then
                                echo ""
                                echo -e "${YELLOW}⚠️  systemd not detected - configuring environment and starting Docker manually...${NC}"
                                
                                # Extract and set environment variables
                                USER_HOME="${HOME:-$(getent passwd "$USER" 2>/dev/null | cut -d: -f6)}"
                                if [ -z "$USER_HOME" ]; then
                                    USER_HOME="$HOME"
                                fi
                                
                                # Extract environment variables from output (compatible with basic grep)
                                # Try to extract from lines like: export XDG_RUNTIME_DIR=/opt/ai-gateway/.docker/run
                                XDG_RUNTIME_DIR=$(echo "$INIT_OUTPUT" | grep "export XDG_RUNTIME_DIR=" | sed -n 's/.*export XDG_RUNTIME_DIR=\([^$]*\).*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"' | tr -d "'")
                                DOCKER_HOST=$(echo "$INIT_OUTPUT" | grep "export DOCKER_HOST=" | sed -n 's/.*export DOCKER_HOST=\([^$]*\).*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"' | tr -d "'")
                                PATH_ADD=$(echo "$INIT_OUTPUT" | grep "export PATH=" | grep -v '\$PATH' | sed -n 's/.*export PATH=\([^$]*\).*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"' | tr -d "'")
                                
                                # Set defaults if not found
                                [ -z "$XDG_RUNTIME_DIR" ] && XDG_RUNTIME_DIR="$USER_HOME/.docker/run"
                                [ -z "$DOCKER_HOST" ] && DOCKER_HOST="unix://$USER_HOME/.docker/run/docker.sock"
                                [ -z "$PATH_ADD" ] && PATH_ADD="/usr/bin"
                                
                                # Export for current session
                                export XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR"
                                export PATH="$PATH_ADD:$PATH"
                                export DOCKER_HOST="$DOCKER_HOST"
                                
                                # Add to .bashrc if not already there
                                if [ -f "$USER_HOME/.bashrc" ] && ! grep -q "# Docker rootless environment" "$USER_HOME/.bashrc" 2>/dev/null; then
                                    echo "" >> "$USER_HOME/.bashrc"
                                    echo "# Docker rootless environment" >> "$USER_HOME/.bashrc"
                                    echo "export XDG_RUNTIME_DIR=\"$XDG_RUNTIME_DIR\"" >> "$USER_HOME/.bashrc"
                                    echo "export PATH=\"$PATH_ADD:\$PATH\"" >> "$USER_HOME/.bashrc"
                                    echo "export DOCKER_HOST=\"$DOCKER_HOST\"" >> "$USER_HOME/.bashrc"
                                fi
                                
                                echo -e "${GREEN}✅ Environment variables configured${NC}"
                                echo ""
                                echo -e "${BLUE}🚀 Starting rootless Docker daemon (without systemd)...${NC}"
                                
                                # Try to start dockerd-rootless.sh in background
                                if command -v dockerd-rootless.sh &>/dev/null; then
                                    # Check if already running
                                    if [ -S "$XDG_RUNTIME_DIR/docker.sock" ] 2>/dev/null; then
                                        echo -e "${GREEN}✅ Docker daemon appears to be running${NC}"
                                        sleep 1
                                        if docker ps &> /dev/null; then
                                            echo -e "${GREEN}✅ Docker: ${version}${NC}"
                                            return 0
                                        fi
                                    fi
                                    
                                    # Start in background
                                    nohup env XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" PATH="$PATH_ADD:$PATH" DOCKER_HOST="$DOCKER_HOST" dockerd-rootless.sh > /dev/null 2>&1 &
                                    DOCKER_PID=$!
                                    sleep 3
                                    
                                    if docker ps &> /dev/null; then
                                        echo -e "${GREEN}✅ Rootless Docker daemon started (PID: $DOCKER_PID)${NC}"
                                        echo -e "${GREEN}✅ Docker: ${version}${NC}"
                                        return 0
                                    else
                                        echo -e "${YELLOW}⚠️  Docker daemon may need more time to start${NC}"
                                        echo -e "${YELLOW}   Check manually: docker ps${NC}"
                                        echo -e "${YELLOW}   Or start manually: dockerd-rootless.sh${NC}"
                                    fi
                                else
                                    echo -e "${YELLOW}⚠️  dockerd-rootless.sh not found${NC}"
                                    echo -e "${YELLOW}   Start manually with:${NC}"
                                    echo -e "${GREEN}   export XDG_RUNTIME_DIR=\"$XDG_RUNTIME_DIR\"${NC}"
                                    echo -e "${GREEN}   export PATH=\"$PATH_ADD:\$PATH\"${NC}"
                                    echo -e "${GREEN}   export DOCKER_HOST=\"$DOCKER_HOST\"${NC}"
                                    echo -e "${GREEN}   dockerd-rootless.sh${NC}"
                                fi
                            else
                                # systemd is available - use systemd
                                # Enable lingering for user (allows user services to run without login)
                                loginctl enable-linger "$USER" 2>/dev/null || true
                                
                                echo ""
                                echo -e "${BLUE}🚀 Starting rootless Docker daemon...${NC}"
                                if systemctl --user start docker 2>/dev/null; then
                                    echo -e "${GREEN}✅ Rootless Docker daemon started${NC}"
                                    # Wait a moment for daemon to be ready
                                    sleep 3
                                    if docker ps &> /dev/null; then
                                        echo -e "${GREEN}✅ Docker: ${version}${NC}"
                                        return 0
                                    else
                                        echo -e "${YELLOW}⚠️  Docker daemon started but not yet ready${NC}"
                                        echo -e "${YELLOW}   Waiting a bit more...${NC}"
                                        sleep 2
                                        if docker ps &> /dev/null; then
                                            echo -e "${GREEN}✅ Docker: ${version}${NC}"
                                            return 0
                                        fi
                                    fi
                                else
                                    echo -e "${YELLOW}⚠️  Failed to start rootless Docker daemon${NC}"
                                    echo -e "${YELLOW}   Try manually: systemctl --user start docker${NC}"
                                fi
                            fi
                        else
                            # Check if there were errors
                            if echo "$INIT_OUTPUT" | grep -qi "error\|failed"; then
                                echo -e "${YELLOW}⚠️  Rootless Docker initialization had issues${NC}"
                                echo -e "${YELLOW}   Check output above for details${NC}"
                                if echo "$INIT_OUTPUT" | grep -qi "subuid\|subgid\|uidmap"; then
                                    echo -e "${YELLOW}   This might be a subuid/subgid configuration issue${NC}"
                                    echo -e "${YELLOW}   Run as root: sudo ./setup_user.sh${NC}"
                                fi
                            else
                                echo -e "${GREEN}✅ Rootless Docker initialized${NC}"
                            fi
                        fi
                    else
                        echo -e "${YELLOW}⚠️  dockerd-rootless-setuptool.sh not found${NC}"
                        echo -e "${YELLOW}   Please install rootless Docker first${NC}"
                        return 1
                    fi
                else
                    echo -e "${YELLOW}⚠️  Rootless Docker initialization skipped by user${NC}"
                    echo -e "${YELLOW}   Run manually: dockerd-rootless-setuptool.sh install${NC}"
                    echo -e "${YELLOW}   Then: systemctl --user start docker${NC}"
                    return 1
                fi
            elif [ "$ROOTLESS_RUNNING" = "false" ]; then
                # Rootless Docker initialized but not running
                echo -e "${BLUE}💡 Rootless Docker is initialized but daemon is not running${NC}"
                echo ""
                
                # Check if systemd is available
                if ! command -v systemctl &>/dev/null || ! systemctl --user list-units &>/dev/null 2>&1; then
                    # systemd not available - use manual startup
                    echo -e "${YELLOW}⚠️  systemd not available - using manual Docker daemon startup${NC}"
                    
                    USER_HOME="${HOME:-$(getent passwd "$USER" 2>/dev/null | cut -d: -f6)}"
                    [ -z "$USER_HOME" ] && USER_HOME="$HOME"
                    
                    # Load environment from .bashrc if available
                    if [ -f "$USER_HOME/.bashrc" ]; then
                        XDG_RUNTIME_DIR=$(grep "export XDG_RUNTIME_DIR=" "$USER_HOME/.bashrc" | sed 's/.*export XDG_RUNTIME_DIR="\([^"]*\)".*/\1/' | head -1)
                        DOCKER_HOST=$(grep "export DOCKER_HOST=" "$USER_HOME/.bashrc" | sed 's/.*export DOCKER_HOST="\([^"]*\)".*/\1/' | head -1)
                        PATH_ADD=$(grep "export PATH=" "$USER_HOME/.bashrc" | grep -v '\$PATH' | sed 's/.*export PATH="\([^"]*\)".*/\1/' | head -1)
                    fi
                    
                    [ -z "$XDG_RUNTIME_DIR" ] && XDG_RUNTIME_DIR="$USER_HOME/.docker/run"
                    [ -z "$DOCKER_HOST" ] && DOCKER_HOST="unix://$USER_HOME/.docker/run/docker.sock"
                    [ -z "$PATH_ADD" ] && PATH_ADD="/usr/bin"
                    
                    export XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR"
                    export PATH="$PATH_ADD:$PATH"
                    export DOCKER_HOST="$DOCKER_HOST"
                    
                    # Ask user interactively (unless in non-interactive mode)
                    if [ "${NON_INTERACTIVE:-0}" = "1" ]; then
                        AUTO_START="y"
                    else
                        if [ ! -t 0 ]; then
                            AUTO_START="y"
                        else
                            read -p "Start rootless Docker daemon now (without systemd)? [Y/n]: " -n 1 -r
                            echo
                            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                                AUTO_START="y"
                            else
                                AUTO_START="n"
                            fi
                        fi
                    fi
                    
                    if [ "$AUTO_START" = "y" ]; then
                        echo ""
                        echo -e "${BLUE}🚀 Starting rootless Docker daemon (without systemd)...${NC}"
                        
                        if command -v dockerd-rootless.sh &>/dev/null; then
                            # Check if already running
                            if [ -S "$XDG_RUNTIME_DIR/docker.sock" ] 2>/dev/null; then
                                echo -e "${GREEN}✅ Docker daemon appears to be running${NC}"
                                sleep 1
                                if docker ps &> /dev/null; then
                                    echo -e "${GREEN}✅ Docker: ${version}${NC}"
                                    return 0
                                fi
                            fi
                            
                            # Start in background
                            nohup env XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" PATH="$PATH_ADD:$PATH" DOCKER_HOST="$DOCKER_HOST" dockerd-rootless.sh > /dev/null 2>&1 &
                            DOCKER_PID=$!
                            sleep 3
                            
                            if docker ps &> /dev/null; then
                                echo -e "${GREEN}✅ Rootless Docker daemon started (PID: $DOCKER_PID)${NC}"
                                echo -e "${GREEN}✅ Docker: ${version}${NC}"
                                return 0
                            else
                                echo -e "${YELLOW}⚠️  Docker daemon may need more time to start${NC}"
                                echo -e "${YELLOW}   Check manually: docker ps${NC}"
                                return 1
                            fi
                        else
                            echo -e "${YELLOW}⚠️  dockerd-rootless.sh not found${NC}"
                            return 1
                        fi
                    else
                        echo -e "${YELLOW}⚠️  Docker daemon start skipped${NC}"
                        return 1
                    fi
                else
                    # systemd is available - use systemd
                    # Ask user interactively (unless in non-interactive mode)
                    if [ "${NON_INTERACTIVE:-0}" = "1" ]; then
                        AUTO_START="n"
                        echo -e "${YELLOW}⚠️  Non-interactive mode: skipping Docker daemon start${NC}"
                        echo -e "${YELLOW}   Run manually: systemctl --user start docker${NC}"
                    else
                        # Check if stdin is available for interactive input
                        if [ ! -t 0 ]; then
                            # stdin is not a terminal, try to start automatically
                            echo -e "${BLUE}ℹ️  Non-interactive terminal detected, attempting to start Docker daemon...${NC}"
                            AUTO_START="y"
                        else
                            read -p "Start rootless Docker daemon now? [Y/n]: " -n 1 -r
                            echo
                            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                                AUTO_START="y"
                            else
                                AUTO_START="n"
                            fi
                        fi
                    fi
                    
                    if [ "$AUTO_START" = "y" ]; then
                        echo ""
                        echo -e "${BLUE}🚀 Starting rootless Docker daemon...${NC}"
                        if systemctl --user start docker 2>/dev/null; then
                            echo -e "${GREEN}✅ Rootless Docker daemon started${NC}"
                            # Wait a moment for daemon to be ready
                            sleep 2
                            if docker ps &> /dev/null; then
                                echo -e "${GREEN}✅ Docker: ${version}${NC}"
                                return 0
                            fi
                        else
                            echo -e "${YELLOW}⚠️  Failed to start rootless Docker daemon${NC}"
                            echo -e "${YELLOW}   Try manually: systemctl --user start docker${NC}"
                            return 1
                        fi
                    else
                        echo -e "${YELLOW}⚠️  Rootless Docker daemon start skipped by user${NC}"
                        echo -e "${YELLOW}   Run manually: systemctl --user start docker${NC}"
                        return 1
                    fi
                fi
            fi
        else
            # Regular Docker (system-wide)
            echo -e "${BLUE}💡 Docker daemon is not running${NC}"
            echo ""
            if [ "${NON_INTERACTIVE:-0}" != "1" ]; then
                read -p "Start Docker daemon now? (requires sudo) [Y/n]: " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                    echo ""
                    echo -e "${BLUE}🚀 Starting Docker daemon...${NC}"
                    if sudo systemctl start docker 2>/dev/null; then
                        echo -e "${GREEN}✅ Docker daemon started${NC}"
                        # Wait a moment for daemon to be ready
                        sleep 2
                        if docker ps &> /dev/null; then
                            echo -e "${GREEN}✅ Docker: ${version}${NC}"
                            return 0
                        fi
                    else
                        echo -e "${YELLOW}⚠️  Failed to start Docker daemon${NC}"
                        echo -e "${YELLOW}   Try manually: sudo systemctl start docker${NC}"
                        return 1
                    fi
                else
                    echo -e "${YELLOW}⚠️  Docker daemon start skipped by user${NC}"
                    echo -e "${YELLOW}   Run manually: sudo systemctl start docker${NC}"
                    return 1
                fi
            else
                echo -e "${YELLOW}⚠️  Non-interactive mode: Docker daemon not running${NC}"
                echo -e "${YELLOW}   Run manually: sudo systemctl start docker${NC}"
                return 1
            fi
        fi
        
        echo ""
        echo -e "${YELLOW}⚠️  Docker daemon is not running${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Docker: ${version}${NC}"
    return 0
}

# Function to check Docker Compose
check_docker_compose() {
    if docker compose version &> /dev/null; then
        local version=$(docker compose version 2>/dev/null | head -n1)
        echo -e "${GREEN}✅ Docker Compose: ${version}${NC}"
        return 0
    elif docker-compose --version &> /dev/null; then
        local version=$(docker-compose --version 2>/dev/null | head -n1)
        echo -e "${GREEN}✅ docker-compose: ${version}${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Docker Compose not found${NC}"
        return 1
    fi
}

# Function to check Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        return 1
    fi
    
    local version=$(python3 --version 2>/dev/null)
    echo -e "${GREEN}✅ ${version}${NC}"
    return 0
}

# Function to check .env file
check_env_file() {
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ .env file not found!${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ .env file found${NC}"
    return 0
}

# Function to check config.yaml
check_config_yaml() {
    if [ ! -f "config.yaml" ]; then
        echo -e "${RED}❌ config.yaml file not found!${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ config.yaml file found${NC}"
    return 0
}

# Function to check virtual environment
check_venv() {
    if [ -d "venv" ] || [ -d ".venv" ]; then
        echo -e "${GREEN}✅ Virtual environment found${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
        return 1
    fi
}

# Function for standard checks
run_standard_checks() {
    local script_type="$1"
    local all_passed=true
    
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    echo ""
    
    # Docker check for scripts working with containers
    if [[ "$script_type" == "start" || "$script_type" == "stop" || "$script_type" == "monitoring" ]]; then
        echo -e "${CYAN}Docker:${NC}"
        if ! check_docker; then
            all_passed=false
        else
            check_docker_compose || all_passed=false
        fi
        echo ""
    fi
    
    # Python check for tests
    if [[ "$script_type" == "test" ]]; then
        echo -e "${CYAN}Python:${NC}"
        check_python || all_passed=false
        echo ""
    fi
    
    # .env check
    if [[ "$script_type" == "start" || "$script_type" == "test" ]]; then
        echo -e "${CYAN}Configuration:${NC}"
        check_env_file || all_passed=false
        if [[ "$script_type" == "test" ]]; then
            check_config_yaml || all_passed=false
        fi
        echo ""
    fi
    
    # Virtual environment for tests
    if [[ "$script_type" == "test" ]]; then
        echo -e "${CYAN}Virtual Environment:${NC}"
        check_venv || all_passed=false
        echo ""
    fi
    
    if [ "$all_passed" = false ]; then
        return 1
    fi
    return 0
}

# Universal function to initialize script with dependency checks
# Usage: init_script_with_checks <script_type> <script_name> <emoji>
# Example: init_script_with_checks "start" "Starting AI Gateway" "🚀"
# This function handles:
# - Setting up colors
# - Loading common initialization module
# - Running dependency checks (Python or bash fallback)
# - Exiting on failure
init_script_with_checks() {
    local script_type="$1"
    local script_name="$2"
    local emoji="${3:-🚀}"
    
    # Ensure colors are set (use defaults if not already set)
    : "${RED:='\033[0;31m'}"
    : "${GREEN:='\033[1;32m'}"
    : "${YELLOW:='\033[1;93m'}"
    : "${BLUE:='\033[1;36m'}"
    : "${NC:='\033[0m'}"
    
    # Load common initialization module if not already loaded
    if ! type print_banner &>/dev/null && ! type run_standard_checks &>/dev/null; then
        if [ -f "src/script_init.sh" ]; then
            source src/script_init.sh
        else
            # Fallback if module not found
            print_banner() {
                local emoji="$1"
                local title="$2"
                echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
                echo -e "${BLUE}║  ${emoji} ${title:<47}║${NC}"
                echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
                echo ""
            }
        fi
    fi
    
    # Check Python before calling Python check module
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        echo -e "${YELLOW}Install Python 3.8+ to use unified checks${NC}"
        echo ""
        # Fallback to bash checks
        print_banner "$emoji" "$script_name"
        if ! run_standard_checks "$script_type"; then
            echo -e "${RED}❌ Dependency check failed${NC}"
            echo -e "${YELLOW}Fix errors and run script again${NC}"
            return 1
        fi
    else
        # Initialize script via unified Python module
        python3 src/check_dependencies.py "$script_type" "$script_name" "$emoji" 2>&1
        CHECK_RESULT=$?
        if [ $CHECK_RESULT -ne 0 ]; then
            echo ""
            echo -e "${RED}❌ Dependency check failed${NC}"
            echo -e "${YELLOW}Fix errors and run script again${NC}"
            return 1
        fi
    fi
    
    return 0
}

