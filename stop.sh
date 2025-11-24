#!/bin/bash
# AI Gateway stop script

set -eo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Non-interactive mode support
if [ "${NON_INTERACTIVE:-0}" = "1" ]; then
    AUTO_YES="y"
else
    AUTO_YES=""
fi

# Colors (always define, even if module is loaded)
RED='\033[0;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;93m'
BLUE='\033[1;36m'
NC='\033[0m'

# Load common initialization module
if [ -f "src/script_init_bash.sh" ]; then
    source src/script_init_bash.sh
else
    # Fallback if module not found
    print_banner() {
        echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║  $1${NC}"
        echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
        echo ""
    }
fi

# Check Python before calling Python check module
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo -e "${YELLOW}Install Python 3.8+ to use unified checks${NC}"
    echo ""
    # Fallback to bash checks
    print_banner "🛑 Stopping AI Gateway"
    if ! run_standard_checks "stop"; then
        echo -e "${RED}❌ Dependency check failed${NC}"
        echo -e "${YELLOW}Fix errors and run script again${NC}"
        exit 1
    fi
else
    # Initialize script via unified Python module
    python3 src/check_dependencies.py stop "Stopping AI Gateway" "🛑" 2>&1
    CHECK_RESULT=$?
    if [ $CHECK_RESULT -ne 0 ]; then
        echo ""
        echo -e "${RED}❌ Dependency check failed${NC}"
        echo -e "${YELLOW}Fix errors and run script again${NC}"
        exit 1
    fi
fi

# Determine command - use array for safe execution
COMPOSE_BASE_CMD=(docker compose)

# Check docker-compose.override.yml
if [ -f "docker-compose.override.yml" ]; then
    COMPOSE_CMD=("${COMPOSE_BASE_CMD[@]}" -f docker-compose.yml -f docker-compose.override.yml)
else
    COMPOSE_CMD=("${COMPOSE_BASE_CMD[@]}" -f docker-compose.yml)
fi

# Check running containers
RUNNING_CONTAINERS=$("${COMPOSE_CMD[@]}" ps -q 2>/dev/null || echo "")

if [ -z "$RUNNING_CONTAINERS" ]; then
    echo -e "${YELLOW}ℹ️  No running containers${NC}"
    echo ""
    echo "Containers are already stopped or were not started."
    exit 0
fi

echo -e "${BLUE}📋 Running containers:${NC}"
"${COMPOSE_CMD[@]}" ps
echo ""

# Confirm stop
if [ -n "${AUTO_YES:-}" ]; then
    REPLY="y"
    echo -e "${BLUE}Non-interactive mode: auto-confirming stop${NC}"
else
    read -p "Stop all containers? [Y/n]: " -n 1 -r
fi
echo
if [[ "${REPLY:-}" =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}Stop cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🛑 Stopping containers...${NC}"
echo ""

# Stop containers
"${COMPOSE_CMD[@]}" down

echo ""
echo -e "${GREEN}✅ Containers stopped!${NC}"
echo ""
echo -e "${BLUE}💡 To start use:${NC}"
echo "  ./start.sh"
echo ""

