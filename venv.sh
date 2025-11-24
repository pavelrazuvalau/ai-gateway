#!/bin/bash
# Script for creating and configuring Python virtual environment

set -o pipefail
# Don't use 'set -e' here - we need to check exit codes manually
# set -e would cause script to exit on any error, even if we handle it
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! cd "$SCRIPT_DIR"; then
    echo "Error: Cannot change to script directory: $SCRIPT_DIR" >&2
    exit 1
fi

VENV_DIR="$SCRIPT_DIR/venv"
VENV_ACTIVATE="$VENV_DIR/bin/activate"

echo "🔧 Setting up Python virtual environment..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Install Python 3.8 or higher:"
    echo "  Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.8 or higher required, found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $(python3 --version) found"

# Create venv if it doesn't exist or is invalid
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_ACTIVATE" ]; then
    if [ -d "$VENV_DIR" ]; then
        echo "⚠️  Virtual environment directory exists but is invalid, recreating..."
        rm -rf "$VENV_DIR"
    fi
    echo "📦 Creating virtual environment..."
    
    # Try to create venv, capture error output for analysis
    # Capture output to analyze error, but check exit code manually
    VENV_ERROR_OUTPUT=$(python3 -m venv "$VENV_DIR" 2>&1)
    VENV_EXIT_CODE=$?
    
    # If command failed, show error
    if [ $VENV_EXIT_CODE -ne 0 ] || [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_ACTIVATE" ]; then
        echo ""
        echo "❌ Failed to create virtual environment"
        echo ""
        
        # Check if it's the ensurepip error
        if echo "$VENV_ERROR_OUTPUT" | grep -qi "ensurepip\|python3-venv"; then
            echo "The python3-venv package is required but not installed."
            echo ""
            echo "On Debian/Ubuntu systems, install it with:"
            echo "  sudo apt install python3-venv"
        else
            # Other error - show the actual error message
            echo "Error details:"
            echo "$VENV_ERROR_OUTPUT" | sed 's/^/  /'
        fi
        echo ""
        exit 1
    fi
    
    # Verify venv was created successfully
    if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_ACTIVATE" ]; then
        echo ""
        echo "❌ Virtual environment directory was not created properly"
        echo ""
        exit 1
    fi
    
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate and install dependencies
echo "📦 Installing dependencies..."
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "❌ Virtual environment activation script not found: $VENV_ACTIVATE" >&2
    exit 1
fi

# shellcheck source=/dev/null
if ! source "$VENV_ACTIVATE"; then
    echo "❌ Failed to activate virtual environment" >&2
    exit 1
fi

# Verify venv is activated
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "❌ Virtual environment is not activated" >&2
    exit 1
fi

if ! pip install --quiet --upgrade pip setuptools wheel; then
    echo "⚠️  Warning: Failed to upgrade pip, continuing anyway..."
fi

if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    if ! pip install --quiet -r "$SCRIPT_DIR/requirements.txt"; then
        echo "❌ Failed to install dependencies from requirements.txt" >&2
        exit 1
    fi
else
    echo "⚠️  requirements.txt not found, installing basic dependencies"
    if ! pip install --quiet colorama pyyaml; then
        echo "❌ Failed to install basic dependencies" >&2
        exit 1
    fi
fi

echo ""
echo "✅ Virtual environment ready!"
echo ""
echo "To activate run:"
echo "  source venv/bin/activate"
echo ""
echo "Or use ./setup.sh and ./start.sh scripts (they activate venv automatically)"


