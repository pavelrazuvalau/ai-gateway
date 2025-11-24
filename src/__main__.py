#!/usr/bin/env python3
"""
AI Gateway - Internal Module Entry Point
Run with: python -m src [command]

This is an internal entry point for advanced users.
For normal use, prefer: ./ai-gateway [command]

Commands:
    setup    - Run interactive setup (default if no command)
    start    - Start Docker containers
    stop     - Stop Docker containers
    update   - Update application files
    --help   - Show help message
"""

import sys
from pathlib import Path

# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Add project root to path so we can import src.*
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import and use CLI
from src.cli import main

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

