#!/usr/bin/env python3
"""
AI Gateway CLI - Unified entry point for all commands.

Usage:
    ./ai-gateway setup     # Run setup (recommended)
    ./ai-gateway start     # Start containers
    ./ai-gateway stop      # Stop containers
    ./ai-gateway update    # Update application files
    ./ai-gateway --help    # Show help

Alternative (for advanced users):
    python3 -m src [command]  # Direct module access

See docs/getting-started.md for detailed information.
"""

import subprocess
import sys
from pathlib import Path

# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Add project root to path so we can import src.*
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_script_path(script_name: str) -> Path:
    """
    Get path to bash script

    Args:
        script_name: Name of the script file

    Returns:
        Path to the script

    Raises:
        FileOperationError: If script not found
    """
    from src.core.exceptions import FileOperationError

    script_path = PROJECT_ROOT / script_name
    if not script_path.exists():
        raise FileOperationError(
            f"Script not found: {script_path}. "
            f"Make sure you're running from the project root directory."
        )
    return script_path


def run_setup() -> int:
    """
    Run setup command.

    Supports --non-interactive flag or NON_INTERACTIVE=1 env var.

    See docs/getting-started.md#step-1-run-setup-script for details.
    """

    from src.application.setup_service import SetupService
    from src.core.exceptions import AIGatewayError
    from src.infrastructure.output import is_non_interactive

    # Check for --non-interactive flag
    non_interactive = "--non-interactive" in sys.argv or is_non_interactive()

    try:
        service = SetupService(PROJECT_ROOT)
        service.run_setup(non_interactive=non_interactive)
        return 0
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return 1
    except AIGatewayError as e:
        print(f"\n❌ Setup failed: {e}")
        print("\n💡 Tip: Check the error message above for details.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        import traceback

        traceback.print_exc()
        return 1


def run_start() -> int:
    """
    Run start command.

    See docs/getting-started.md#step-2-start-the-system for details.
    """
    from src.application.start_service import StartService
    from src.core.exceptions import AIGatewayError, DockerError

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

        # Check if models are available and suggest Continue.dev setup
        service.check_models_and_suggest_continue_dev()

        return 0
    except KeyboardInterrupt:
        print("\n\n❌ Start cancelled by user")
        return 1
    except DockerError as e:
        print(f"\n❌ Docker error: {e}")
        print("\n💡 Tip: Make sure Docker is running and you have permissions.")
        print("   Try: docker compose ps")
        return 1
    except AIGatewayError as e:
        print(f"\n❌ Error starting containers: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


def run_stop() -> int:
    """Run stop command"""
    from src.core.exceptions import AIGatewayError, FileOperationError

    try:
        script = get_script_path("stop.sh")
        result = subprocess.run(
            ["bash", str(script)], cwd=str(PROJECT_ROOT), check=False
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n❌ Stop cancelled by user")
        return 1
    except FileOperationError as e:
        print(f"\n❌ Script not found: {e}")
        return 1
    except AIGatewayError as e:
        print(f"\n❌ Error stopping containers: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


def run_continue_dev() -> int:
    """
    Run Continue.dev configuration command.

    Supports --non-interactive flag or NON_INTERACTIVE=1 env var.

    See docs/integrations/continue-dev.md for details.
    """
    from src.application.continue_dev_service import ContinueDevService
    from src.core.exceptions import AIGatewayError
    from src.infrastructure.output import is_non_interactive

    # Check for --non-interactive flag
    non_interactive = "--non-interactive" in sys.argv or is_non_interactive()

    try:
        service = ContinueDevService(PROJECT_ROOT)
        return service.run_setup_interactive(non_interactive=non_interactive)
    except KeyboardInterrupt:
        print("\n\n❌ Continue.dev setup cancelled by user")
        return 1
    except AIGatewayError as e:
        print(f"\n❌ Continue.dev setup failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


def run_update(args: list) -> int:
    """Run update command"""
    from src.core.exceptions import AIGatewayError, FileOperationError

    try:
        script = get_script_path("update.sh")
        cmd = ["bash", str(script)] + args
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n❌ Update cancelled by user")
        return 1
    except FileOperationError as e:
        print(f"\n❌ Script not found: {e}")
        return 1
    except AIGatewayError as e:
        print(f"\n❌ Error updating: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
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
    print("  continue-dev       Generate Continue.dev configuration")
    print("  update [args...]   Update application files")
    print("                     (optional: SOURCE_DIR APP_DIR USERNAME)")
    print("  --help, -h         Show this help message")
    print()
    print("Examples:")
    print("  ./ai-gateway setup")
    print("  ./ai-gateway start")
    print("  ./ai-gateway stop")
    print("  ./ai-gateway continue-dev")
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
    elif command == "continue-dev":
        return run_continue_dev()
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
    from src.core.exceptions import AIGatewayError

    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except AIGatewayError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
