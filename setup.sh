#!/bin/bash
# AI Gateway Setup Script for Linux/macOS
# Wrapper script that sets up venv and runs setup module
# Uses venv.sh to avoid code duplication

set -eo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! cd "$SCRIPT_DIR"; then
    echo "Error: Cannot change to script directory: $SCRIPT_DIR" >&2
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;93m'
BLUE='\033[1;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 AI Gateway - Quick Setup (Linux/macOS)               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Use venv.sh to create/update venv (avoids code duplication)
if [ -f "$SCRIPT_DIR/venv.sh" ]; then
    if ! "$SCRIPT_DIR/venv.sh" 2>&1; then
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
    VENV_DIR="$SCRIPT_DIR/venv"
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
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip install --quiet -r "$SCRIPT_DIR/requirements.txt" || exit 1
    fi
fi

# Activate venv (venv.sh may have created it but not activated in this shell)
VENV_ACTIVATE="$SCRIPT_DIR/venv/bin/activate"
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

# Run setup module
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Starting setup...                                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Run setup via CLI entry point
# Use ./ai-gateway script (standard production practice)
if ! "$SCRIPT_DIR/ai-gateway" setup; then
    echo -e "${RED}❌ Setup failed${NC}"
    exit 1
fi

# Ask about Continue.dev setup
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Continue.dev Setup (Optional)                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}💡 Continue.dev is a VS Code extension for AI-powered coding${NC}"
echo -e "${BLUE}   The setup script will:${NC}"
echo -e "   • Configure Continue.dev with models from LiteLLM API"
echo -e "   • Install VS Code extension (if VS Code is available)"
echo -e "   • Optimize context to exclude large MD files"
echo -e "   • Create system prompt to avoid duplication"
echo ""
read -p "Setup Continue.dev? [y/N]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "$SCRIPT_DIR/scripts/setup_continue_dev.sh" ]; then
        if bash "$SCRIPT_DIR/scripts/setup_continue_dev.sh"; then
            echo ""
            echo -e "${GREEN}✅ Continue.dev setup completed!${NC}"
        else
            echo ""
            echo -e "${YELLOW}⚠️  Continue.dev setup had some issues, but you can run it manually:${NC}"
            echo -e "   ${GREEN}bash scripts/setup_continue_dev.sh${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Continue.dev setup script not found${NC}"
    fi
else
    echo -e "${BLUE}💡 You can setup Continue.dev later by running:${NC}"
    echo -e "   ${GREEN}bash scripts/setup_continue_dev.sh${NC}"
fi
