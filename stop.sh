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

# Load common initialization module
if [ -f "src/script_init.sh" ]; then
    source src/script_init.sh
fi

# Run dependency checks using unified function
if ! init_script_with_checks "stop" "Stopping AI Gateway" "🛑"; then
    exit 1
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

