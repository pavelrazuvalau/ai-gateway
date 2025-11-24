"""
Utility functions for colors, formatting, and common operations
DEPRECATED: Use infrastructure.logger for new code, but kept for backward compatibility
"""

import os
import sys
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path

# Try to import colorama, fallback to empty strings if not available
try:
    from colorama import init, Fore, Style
    # Initialize colorama for cross-platform color support
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback when colorama is not available
    COLORAMA_AVAILABLE = False
    # Create dummy classes for Fore and Style
    class Fore:
        RED = ''
        GREEN = ''
        LIGHTGREEN_EX = ''
        YELLOW = ''
        LIGHTYELLOW_EX = ''
        BLUE = ''
        LIGHTCYAN_EX = ''
        CYAN = ''
        MAGENTA = ''
    
    class Style:
        RESET_ALL = ''
        BRIGHT = ''


class Colors:
    """Color constants for terminal output"""
    RED = Fore.RED if COLORAMA_AVAILABLE else '\033[0;31m'
    GREEN = Fore.GREEN if COLORAMA_AVAILABLE else '\033[1;32m'
    YELLOW = Fore.YELLOW if COLORAMA_AVAILABLE else '\033[1;33m'
    BLUE = Fore.BLUE if COLORAMA_AVAILABLE else '\033[1;34m'
    CYAN = Fore.CYAN if COLORAMA_AVAILABLE else '\033[1;36m'
    RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else '\033[0m'


def print_error(text: str) -> None:
    """Print error message in red"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_success(text: str) -> None:
    """Print success message in green"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text: str) -> None:
    """Print info message in blue"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def print_step(text: str) -> None:
    """Print step message"""
    # Try to use logger if available
    try:
        from .infrastructure.logger import get_logger
        _logger = get_logger(__name__)
        _logger.info(f"📋 {text}")
    except ImportError:
        print(f"{Colors.CYAN}📋 {text}{Colors.RESET}")


def print_header(text: str) -> None:
    """Print header with banner"""
    banner_text = str(text)
    # Create banner
    print(f"{Colors.BLUE}╔{'═' * 58}╗{Colors.RESET}")
    print(f"{Colors.BLUE}║  {banner_text:<55}║{Colors.RESET}")
    print(f"{Colors.BLUE}╚{'═' * 58}╝{Colors.RESET}")


def _ask_yes_no(prompt: str, default: bool = True) -> bool:
    """
    Ask user yes/no question
    
    Args:
        prompt: Question to ask
        default: Default value if user just presses Enter
        
    Returns:
        True if yes, False if no
    """
    default_text = "[Y/n]" if default else "[y/N]"
    try:
        response = input(f"{prompt} {default_text}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ('y', 'yes')
    except (EOFError, KeyboardInterrupt):
        return not default  # Return opposite of default on interrupt


def check_root() -> None:
    """Check if script is run as root and offer to create system user or switch to existing one"""
    if os.geteuid() == 0:
        # Try relative import first, fallback to absolute
        try:
            from ..core.constants import SYSTEM_USERNAME, SYSTEM_APP_DIR, SUBPROCESS_TIMEOUT
        except ImportError:
            from src.core.constants import SYSTEM_USERNAME, SYSTEM_APP_DIR, SUBPROCESS_TIMEOUT
        
        # Check if we're running from user's location (not /opt/ai-gateway)
        script_dir = Path(__file__).parent.parent.resolve()
        app_dir = Path(SYSTEM_APP_DIR)
        
        # If running from user's location (not /opt), offer to setup user and copy to /opt
        if script_dir != app_dir:
            print_warning("⚠️  Running setup as root from user location")
            print()
            print(f"💡 You're running from: {script_dir}")
            print(f"   This is not the system installation directory ({SYSTEM_APP_DIR})")
            print()
            print("Options:")
            print("  1. Create system user and copy files to /opt/ai-gateway (recommended for production)")
            print("  2. Switch to a regular user to run from current location")
            print()
            
            # Check if user.sh exists
            setup_user_script = script_dir / "user.sh"
            if setup_user_script.exists() and os.access(setup_user_script, os.X_OK):
                print(f"Would you like to run user.sh to:")
                print(f"  • Create system user '{SYSTEM_USERNAME}'")
                print(f"  • Copy files to {SYSTEM_APP_DIR}")
                print(f"  • Set proper permissions")
                print()
                
                response = _ask_yes_no("Run user.sh now?", default=True)
                if response:
                    print()
                    print("🚀 Running user.sh...")
                    print()
                    
                    try:
                        result = subprocess.run(
                            [str(setup_user_script)],
                            cwd=str(script_dir),
                            timeout=SUBPROCESS_TIMEOUT * 60,
                            check=False
                        )
                        
                        if result.returncode != 0:
                            print_error("user.sh failed")
                            print()
                            print("You can run it manually:")
                            print(f"  sudo {setup_user_script}")
                            sys.exit(1)
                        
                        print()
                        print_success(f"System user '{SYSTEM_USERNAME}' created and files copied to {SYSTEM_APP_DIR}!")
                        print()
                        print("Next steps:")
                        print(f"  1. Switch to the new user: sudo -u {SYSTEM_USERNAME} -s")
                        print(f"  2. Navigate to: cd {SYSTEM_APP_DIR}")
                        print(f"  3. Run setup: ./setup.sh (or ./ai-gateway setup)")
                        print()
                        sys.exit(0)
                        
                    except subprocess.TimeoutExpired:
                        print_error("user.sh timed out")
                        print()
                        print("You can run it manually:")
                        print(f"  sudo {setup_user_script}")
                        sys.exit(1)
                    except KeyboardInterrupt:
                        print("\n\nSetup cancelled by user")
                        sys.exit(1)
                    except Exception as e:
                        print_error(f"Error running user.sh: {e}")
                        print()
                        print("You can run it manually:")
                        print(f"  sudo {setup_user_script}")
                        sys.exit(1)
                else:
                    print()
                    print("To run setup from your current location:")
                    print("  1. Switch to a regular user: su - your_user")
                    print("  2. Run: ./setup.sh (or ./ai-gateway setup)")
                    print()
                    sys.exit(0)
            else:
                print("user.sh not found. To run setup from your current location:")
                print("  1. Switch to a regular user: su - your_user")
                print("  2. Run: ./setup.sh (or python3 -m src)")
                print()
                sys.exit(1)
        
        # Running from /opt/ai-gateway as root - offer system user setup
        print_error("ERROR: Do not run this script as root!")
        print()
        print_warning("This script should be run as a regular user.")
        print()
        
        # Check if system user already exists
        try:
            import pwd
            try:
                pwd.getpwnam(SYSTEM_USERNAME)
                user_exists = True
            except KeyError:
                user_exists = False
        except ImportError:
            # Fallback: check via subprocess
            result = subprocess.run(
                ["id", SYSTEM_USERNAME],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            user_exists = (result.returncode == 0)
        
        if user_exists:
            # User already exists - offer to switch to it
            print(f"✅ System user '{SYSTEM_USERNAME}' already exists!")
            print()
            
            # Check if we're running from a different location than SYSTEM_APP_DIR
            script_dir = Path(__file__).parent.parent.resolve()
            app_dir = Path(SYSTEM_APP_DIR)
            current_setup = script_dir / "setup.sh"
            app_setup = app_dir / "setup.sh"
            
            # Check if files in /opt/ai-gateway need updating
            needs_update = False
            update_reason = ""
            
            if app_dir.exists() and app_setup.exists():
                # Check if source directory is a git repo and compare with app_dir
                if (script_dir / ".git").exists():
                    try:
                        source_hash = subprocess.run(
                            ["git", "-C", str(script_dir), "rev-parse", "HEAD"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        ).stdout.strip()
                        
                        if (app_dir / ".git").exists():
                            app_hash = subprocess.run(
                                ["git", "-C", str(app_dir), "rev-parse", "HEAD"],
                                capture_output=True,
                                text=True,
                                timeout=5
                            ).stdout.strip()
                            
                            if source_hash and app_hash and source_hash != app_hash:
                                needs_update = True
                                update_reason = "source code is newer (different git commits)"
                        elif source_hash:
                            # App dir is not a git repo, check modification time
                            if (script_dir / "src" / "ports.py").exists() and (app_dir / "src" / "ports.py").exists():
                                source_mtime = (script_dir / "src" / "ports.py").stat().st_mtime
                                app_mtime = (app_dir / "src" / "ports.py").stat().st_mtime
                                if source_mtime > app_mtime:
                                    needs_update = True
                                    update_reason = "source code is newer (file modification time)"
                    except Exception:
                        pass  # Ignore errors in update check
            
            if needs_update:
                print_warning(f"⚠️  Files in {SYSTEM_APP_DIR} may be outdated!")
                print(f"   Reason: {update_reason}")
                print()
                print(f"💡 We recommend updating {SYSTEM_APP_DIR} before running setup.")
                print("   This will ensure you have the latest code with all features.")
                print()
                
                if _ask_yes_no("Update files in /opt/ai-gateway first?", default=True):
                    print()
                    print("🔄 Updating files in /opt/ai-gateway...")
                    print()
                    
                    # Run user.sh to update files
                    setup_user_script = script_dir / "user.sh"
                    if setup_user_script.exists() and setup_user_script.is_file():
                        try:
                            result = subprocess.run(
                                [str(setup_user_script)],
                                cwd=str(script_dir),
                                timeout=SUBPROCESS_TIMEOUT * 60,
                                check=False
                            )
                            
                            if result.returncode == 0:
                                print()
                                print_success("Files updated successfully!")
                                print()
                            else:
                                print()
                                print_warning(f"Update completed with exit code {result.returncode}.")
                                print("   Check the output above for specific warnings or errors.")
                                print()
                        except Exception as e:
                            print_warning(f"Update check failed: {e}")
                            print("Continuing with existing files...")
                            print()
                    else:
                        print_warning("user.sh not found, skipping update")
                        print()
            
            print(f"💡 We can automatically run setup as user '{SYSTEM_USERNAME}'.")
            print("   This will:")
            print("   • Run the setup script from the correct location")
            print(f"   • Use the application directory: {SYSTEM_APP_DIR}")
            print("   • Configure the application properly")
            print()
            
            if _ask_yes_no(f"Run setup as user '{SYSTEM_USERNAME}'?", default=True):
                print()
                print(f"🚀 Running setup as user '{SYSTEM_USERNAME}'...")
                print()
                
                # Always use setup script from SYSTEM_APP_DIR
                setup_script = app_setup
                
                # Fallback to current directory if app_dir doesn't exist
                if not setup_script.exists():
                    setup_script = current_setup
                
                if setup_script.exists() and setup_script.is_file():
                    try:
                        # Run setup.sh as system user
                        result = subprocess.run(
                            ["sudo", "-u", SYSTEM_USERNAME, str(setup_script)],
                            cwd=str(setup_script.parent),
                            timeout=SUBPROCESS_TIMEOUT * 60,  # 5 minutes timeout
                            check=False
                        )
                        
                        if result.returncode == 0:
                            print()
                            print_success("Setup completed successfully!")
                            sys.exit(0)
                        else:
                            print()
                            print_warning("Setup completed with warnings or errors.")
                            sys.exit(result.returncode)
                    except subprocess.TimeoutExpired:
                        print_error("Setup timed out")
                        sys.exit(1)
                    except KeyboardInterrupt:
                        print("\n\nSetup cancelled by user")
                        sys.exit(1)
                    except Exception as e:
                        print_error(f"Error running setup: {e}")
                        sys.exit(1)
                else:
                    print_error(f"Setup script not found: {setup_script}")
                    print()
                    print("Please run setup manually:")
                    print(f"  sudo -u {SYSTEM_USERNAME} {SYSTEM_APP_DIR}/setup.sh")
                    sys.exit(1)
            else:
                print()
                print("Setup cancelled.")
                print()
                print("Alternative options:")
                print(f"  1. Run setup manually: sudo -u {SYSTEM_USERNAME} {SYSTEM_APP_DIR}/setup.sh")
                print(f"  2. Switch to user: sudo -u {SYSTEM_USERNAME} -s")
                sys.exit(1)
        
        # User doesn't exist - offer to create it
        print("For production deployment, we recommend creating a dedicated system user.")
        print()
        
        # Check if user.sh exists
        try:
            script_dir = Path(__file__).parent.parent.resolve()
            setup_user_script = script_dir / "user.sh"
            
            # Validate path
            if not setup_user_script.exists():
                raise FileNotFoundError(f"user.sh not found in {script_dir}")
            
            if not os.access(setup_user_script, os.X_OK):
                raise PermissionError(f"user.sh is not executable: {setup_user_script}")
            
            print(f"💡 We can create a system user '{SYSTEM_USERNAME}' (like www-data) for you.")
            print("   This user will:")
            print("   • Have no login shell (secure)")
            print(f"   • Own the application files in {SYSTEM_APP_DIR}")
            print("   • Have Docker access (rootless preferred)")
            print("   • Have systemd service configured")
            print()
            
            if not _ask_yes_no("Create system user and setup?", default=True):
                print()
                print("Setup cancelled.")
                print()
                print("Alternative options:")
                print("  1. Switch to a regular user: su - your_user")
                print(f"  2. Run user.sh manually: sudo {setup_user_script}")
                sys.exit(1)
            
            print()
            print("🚀 Running user.sh...")
            print()
            
            # Run user.sh with timeout
            try:
                result = subprocess.run(
                    [str(setup_user_script)],
                    cwd=str(script_dir),
                    timeout=SUBPROCESS_TIMEOUT * 60,  # 5 minutes timeout
                    check=False
                )
                
                if result.returncode != 0:
                    print_error("setup_user.sh failed")
                    sys.exit(1)
                
                print()
                print_success(f"System user '{SYSTEM_USERNAME}' created successfully!")
                print()
                
                # Check if setup.sh exists in SYSTEM_APP_DIR
                app_dir = Path(SYSTEM_APP_DIR)
                setup_script = app_dir / "setup.sh"
                
                if setup_script.exists() and setup_script.is_file():
                    print(f"📋 Application files are in: {SYSTEM_APP_DIR}")
                    print()
                    print(f"Would you like to run the initial setup now as user '{SYSTEM_USERNAME}'?")
                    print("   (This will configure the application)")
                    print()
                    
                    if _ask_yes_no("Run setup now?", default=True):
                        print()
                        print(f"🚀 Running setup as user '{SYSTEM_USERNAME}'...")
                        print()
                        
                        try:
                            # Run setup.sh as system user with timeout
                            result = subprocess.run(
                                ["sudo", "-u", SYSTEM_USERNAME, str(setup_script)],
                                cwd=str(app_dir),
                                timeout=SUBPROCESS_TIMEOUT * 60,  # 5 minutes timeout
                                check=False
                            )
                            
                            if result.returncode == 0:
                                print()
                                print_success("Setup completed successfully!")
                                print()
                                print("You can now start the service:")
                                print(f"  sudo -u {SYSTEM_USERNAME} {SYSTEM_APP_DIR}/start.sh")
                                print()
                                print("Or use systemd service:")
                                print(f"  sudo systemctl start ai-gateway  # for regular Docker")
                                print(f"  sudo -u {SYSTEM_USERNAME} systemctl --user start ai-gateway  # for rootless Docker")
                            else:
                                print()
                                print_warning("Setup completed with warnings.")
                                print("You can run it manually:")
                                print(f"  sudo -u {SYSTEM_USERNAME} {setup_script}")
                        except subprocess.TimeoutExpired:
                            print_error("Setup timed out")
                            print("You can run it manually:")
                            print(f"  sudo -u {SYSTEM_USERNAME} {setup_script}")
                        except KeyboardInterrupt:
                            print("\n\nSetup cancelled by user")
                        except Exception as e:
                            print_error(f"Error running setup: {e}")
                            print()
                            print("You can run it manually:")
                            print(f"  sudo -u {SYSTEM_USERNAME} {setup_script}")
                    else:
                        print()
                        print("Setup skipped. You can run it later:")
                        print(f"  sudo -u {SYSTEM_USERNAME} {setup_script}")
                else:
                    print("Next steps:")
                    print(f"  1. Switch to the new user: sudo -u {SYSTEM_USERNAME} -s")
                    print(f"  2. Navigate to: cd {SYSTEM_APP_DIR}")
                    print(f"  3. Run setup: sudo -u {SYSTEM_USERNAME} {SYSTEM_APP_DIR}/setup.sh")
                    print()
                
                sys.exit(0)
                
            except subprocess.TimeoutExpired:
                print_error("setup_user.sh timed out")
                print()
                print("You can run it manually:")
                print(f"  sudo {setup_user_script}")
                sys.exit(1)
            except KeyboardInterrupt:
                print("\n\nSetup cancelled by user")
                sys.exit(1)
            except (FileNotFoundError, PermissionError, ValueError) as e:
                print_error(f"Error: {e}")
                print()
                print("You can run user.sh manually:")
                print(f"  sudo {setup_user_script}")
                sys.exit(1)
            except Exception as e:
                print_error(f"Unexpected error running user.sh: {e}")
                print()
                print("You can run it manually:")
                print(f"  sudo {setup_user_script}")
                sys.exit(1)
                
        except (FileNotFoundError, PermissionError):
            # user.sh not found or not executable
            print("If you're in the docker group, switch to a regular user:")
            print("  su - your_user")
            print("  ./setup.sh (or ./ai-gateway setup)")
            print()
            if 'setup_user_script' in locals() and setup_user_script.exists():
                print(f"Or run user.sh manually: sudo {setup_user_script}")
            sys.exit(1)


def get_user() -> str:
    """Get current username"""
    return os.getenv("USER", os.getenv("USERNAME", "unknown"))


def read_env_file(file_path: str = ".env") -> Dict[str, str]:
    """
    Read environment variables from .env file
    
    Args:
        file_path: Path to .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars: Dict[str, str] = {}
    
    if not os.path.exists(file_path):
        return env_vars
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    env_vars[key] = value
    except Exception as e:
        print_warning(f"Error reading .env file: {e}")
    
    return env_vars


def set_file_permissions(file_path: str, mode: int = 0o600) -> None:
    """
    Set file permissions
    
    Args:
        file_path: Path to file
        mode: Permission mode (octal, default 0o600)
    """
    try:
        os.chmod(file_path, mode)
    except (OSError, PermissionError) as e:
        print_warning(f"Failed to set permissions on {file_path}: {e}")


def ensure_dir(dir_path: str) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        dir_path: Path to directory
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        print_error(f"Failed to create directory {dir_path}: {e}")
        raise
