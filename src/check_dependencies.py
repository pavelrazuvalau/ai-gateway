#!/usr/bin/env python3
"""
Unified dependency check script for all platforms
Used by bash and batch scripts for consistent checks
"""

import json
import os
import sys

# Add project root to path so we can import src.*
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Now import from src package
from src.script_init import ScriptInit, ScriptType  # noqa: E402


def main():
    """Main entry point for dependency checks"""
    if len(sys.argv) < 2:
        print("Usage: check_dependencies.py <script_type> [script_name] [emoji]")
        print("  script_type: start|stop|test|setup|monitoring")
        print("  script_name: Display name (optional)")
        print("  emoji: Emoji for banner (optional)")
        sys.exit(1)

    script_type_str = sys.argv[1].lower()
    script_name = sys.argv[2] if len(sys.argv) > 2 else None
    emoji = sys.argv[3] if len(sys.argv) > 3 else "🚀"

    # Map string to ScriptType
    type_map = {
        "start": ScriptType.START,
        "stop": ScriptType.STOP,
        "test": ScriptType.TEST,
        "setup": ScriptType.SETUP,
        "monitoring": ScriptType.MONITORING,
    }

    script_type = type_map.get(script_type_str, ScriptType.OTHER)

    # Default script names
    if not script_name:
        name_map = {
            "start": "Starting AI Gateway",
            "stop": "Stopping AI Gateway",
            "test": "Testing models via LiteLLM Gateway",
            "setup": "LiteLLM + Open WebUI + PostgreSQL - Setup",
            "monitoring": "Monitoring AI Gateway",
        }
        script_name = name_map.get(script_type_str, "AI Gateway")

    # Initialize script
    script_init = ScriptInit(script_name, script_type, SCRIPT_DIR)
    script_init.print_banner(emoji)

    # Run standard checks
    success = script_init.run_standard_checks()

    # Output result as JSON for programmatic use (only if needed)
    # JSON output is suppressed for user-facing scripts
    # If needed programmatically, it can be enabled via environment variable
    if os.environ.get("CHECK_DEPS_JSON_OUTPUT", "").lower() == "true":
        result = {
            "success": success,
            "script_type": script_type_str,
            "script_name": script_name,
        }
        # Print JSON to stderr so stdout can be used for other purposes
        print(json.dumps(result), file=sys.stderr)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
