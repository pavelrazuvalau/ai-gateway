#!/usr/bin/env python3
"""
Universal Virtual Key Setup Script
Works on all platforms (Linux, macOS, Windows)

Usage:
    python3 setup_virtual_key.py        # Linux/macOS
    python setup_virtual_key.py         # Windows
    python -m src.setup_virtual_key     # As module
"""

import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.absolute()

# Add project root to path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import and run main function
from src.setup_virtual_key import main

if __name__ == "__main__":
    sys.exit(main())

