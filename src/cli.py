#!/usr/bin/env python3
"""
AI Gateway CLI - Unified entry point for all commands
Usage:
    ./ai-gateway setup     # Run setup (recommended)
    ./ai-gateway start     # Start containers
    ./ai-gateway stop      # Stop containers
    ./ai-gateway update    # Update application files
    ./ai-gateway --help    # Show help
    
Alternative (for advanced users):
    python3 -m src [command]  # Direct module access
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Add project root to path so we can import src.*
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_script_path(script_name: str) -> Path:
    """Get path to bash script"""
    script_path = PROJECT_ROOT / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    return script_path


def run_setup() -> int:
    """Run setup command"""
    from src.application.setup_service import SetupService
    
    try:
        service = SetupService(PROJECT_ROOT)
        service.run_setup()
        return 0
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def run_start() -> int:
    """Run start command"""
    from src.application.start_service import StartService
    
    try:
        service = StartService(PROJECT_ROOT)
        
        # Start containers and wait for health
        if not service.start_containers(wait_for_healthy=True):
            return 1
        
        # Check for errors
        has_errors, errors = service.check_container_status()
        if has_errors:
            print()
            print("⚠️  Some containers may have errors:")
            for error in errors:
                print(f"   • {error}")
            print()
            print("📋 Diagnostic commands:")
            print("   docker compose logs")
            print("   docker compose ps")
            print()
            return 1
        
        # Print access information
        service.print_access_info()
        
        # Check for first run and show Virtual Key setup instructions
        service.show_first_run_instructions()
        
        return 0
    except KeyboardInterrupt:
        print("\n\n❌ Start cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def run_stop() -> int:
    """Run stop command"""
    script = get_script_path("stop.sh")
    try:
        result = subprocess.run(
            ["bash", str(script)],
            cwd=str(PROJECT_ROOT),
            check=False
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n❌ Stop cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def run_update(args: list) -> int:
    """Run update command"""
    script = get_script_path("update.sh")
    try:
        cmd = ["bash", str(script)] + args
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            check=False
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n❌ Update cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def show_help() -> None:
    """Show help message"""
    print("AI Gateway - Unified CLI")
    print()
    print("Usage:")
    print("  ./ai-gateway <command> [options]")
    print()
    print("Commands:")
    print("  setup              Run interactive setup")
    print("  start              Start Docker containers")
    print("  stop               Stop Docker containers")
    print("  update [args...]   Update application files")
    print("                     (optional: SOURCE_DIR APP_DIR USERNAME)")
    print("  --help, -h         Show this help message")
    print()
    print("Examples:")
    print("  ./ai-gateway setup")
    print("  ./ai-gateway start")
    print("  ./ai-gateway stop")
    print("  ./ai-gateway update")
    print("  ./ai-gateway update /path/to/source /opt/ai-gateway aigateway")
    print()
    print("Alternative entry points:")
    print("  ./setup.sh         # Setup wrapper (calls ./ai-gateway setup)")
    print("  ./start.sh         # Start containers")
    print("  ./stop.sh          # Stop containers")
    print("  ./update.sh        # Update files")
    print()
    print("Advanced (direct module access):")
    print("  python3 -m src [command]  # Direct Python module access")


def main() -> int:
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        # No command specified - default to setup (backward compatibility)
        return run_setup()
    
    command = sys.argv[1].lower()
    
    if command in ["--help", "-h", "help"]:
        show_help()
        return 0
    elif command == "setup":
        return run_setup()
    elif command == "start":
        return run_start()
    elif command == "stop":
        return run_stop()
    elif command == "update":
        # Pass remaining args to update script
        update_args = sys.argv[2:] if len(sys.argv) > 2 else []
        return run_update(update_args)
    else:
        print(f"❌ Unknown command: {command}")
        print()
        show_help()
        return 1


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

