#!/bin/bash
# Continue.dev Configuration Generator
# Wrapper script that sets up venv and runs Continue.dev setup module
# Usage: ./continue-dev.sh

set -eo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

if ! cd "$PROJECT_ROOT"; then
    echo "Error: Cannot change to project root directory: $PROJECT_ROOT" >&2
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;93m'
BLUE='\033[1;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔧 Continue.dev Configuration Generator                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Use venv.sh to create/update venv (avoids code duplication)
if [ -f "$PROJECT_ROOT/venv.sh" ]; then
    if ! "$PROJECT_ROOT/venv.sh" 2>&1; then
        # venv.sh already prints detailed error messages, just exit
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  venv.sh not found, falling back to direct venv creation${NC}"
    # Fallback: basic Python check
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        echo ""
        echo "Install Python 3.8 or higher:"
        echo "  Fedora/RHEL: sudo dnf install python3 python3-pip python3-venv"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "  Arch: sudo pacman -S python python-pip"
        echo "  macOS: brew install python@3.11"
        exit 1
    fi
    
    # Create venv directly
    VENV_DIR="$PROJECT_ROOT/venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${BLUE}📦 Creating virtual environment...${NC}"
        if ! python3 -m venv "$VENV_DIR" 2>&1; then
            echo -e "${RED}❌ Failed to create virtual environment${NC}"
            exit 1
        fi
    fi
    
    # Activate and install dependencies
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    pip install --quiet --upgrade pip setuptools wheel 2>/dev/null || true
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install --quiet -r "$PROJECT_ROOT/requirements.txt" || exit 1
    fi
fi

# Activate venv (venv.sh may have created it but not activated in this shell)
VENV_ACTIVATE="$PROJECT_ROOT/venv/bin/activate"
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo -e "${RED}❌ Virtual environment activation script not found${NC}"
    exit 1
fi

# shellcheck source=/dev/null
source "$VENV_ACTIVATE"

# Verify venv is activated
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo -e "${RED}❌ Virtual environment is not activated${NC}"
    exit 1
fi

# Run Continue.dev setup via CLI entry point
# Use ./ai-gateway script (standard production practice)
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Starting Continue.dev configuration...                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

if ! "$PROJECT_ROOT/ai-gateway" continue-dev; then
    echo -e "${RED}❌ Continue.dev setup failed${NC}"
    exit 1
fi
