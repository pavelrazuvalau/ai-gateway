#!/bin/bash
# Script to setup Virtual Key for Open WebUI
# Wrapper for universal Python script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Run setup.sh first to generate configuration"
    exit 1
fi

# Run the universal Python script
if [ -f "virtual-key.py" ]; then
    python3 virtual-key.py
else
    # Fallback to module import
    python3 -m src.virtual_key
fi

