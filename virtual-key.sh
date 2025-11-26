#!/bin/bash
# Script to setup Virtual Key for Open WebUI
# Wrapper for Python module

set -eo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load common initialization module
if [ -f "src/script_init.sh" ]; then
    source src/script_init.sh
fi

# Run dependency checks using unified function
if ! init_script_with_checks "setup" "Virtual Key Setup" "🔑"; then
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo ""
    echo -e "${YELLOW}Environment needs to be configured first.${NC}"
    echo ""
    echo -e "${BLUE}Run setup to configure:${NC}"
    echo -e "${GREEN}   ./setup.sh${NC}"
    echo ""
    exit 1
fi

# Run the Python module
python3 -m src.virtual_key

