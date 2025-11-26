"""
Common initialization module for all scripts.

Provides consistency in checks and headers.

See docs/getting-started.md for general information.
See docs/getting-started.md#if-dependencies-are-missing for dependency checks.
"""

import os
import sys
import subprocess
from typing import Optional, Dict, List, Tuple
from enum import Enum

# Import from src package (works both as module and when imported from check_dependencies.py)
try:
    from .utils import (
        print_header, print_success, print_info, print_warning, print_error, Colors
    )
    from .platform_utils import detect_platform, PlatformType
except ImportError:
    # Fallback for absolute imports when run as script
    from src.utils import (
        print_header, print_success, print_info, print_warning, print_error, Colors
    )
    from src.platform_utils import detect_platform, PlatformType


class ScriptType(Enum):
    """Script types for customizing checks"""
    SETUP = "setup"
    START = "start"
    STOP = "stop"
    TEST = "test"
    MONITORING = "monitoring"
    OTHER = "other"


class ScriptInit:
    """Class for initializing scripts with uniform checks"""
    
    def __init__(self, script_name: str, script_type: ScriptType, script_dir: Optional[str] = None):
        """
        Initialize script
        
        Args:
            script_name: Script name for display
            script_type: Script type (for customizing checks)
            script_dir: Script directory (if None, determined automatically)
        """
        self.script_name = script_name
        self.script_type = script_type
        self.script_dir = script_dir or os.path.dirname(os.path.abspath(sys.argv[0]))
        self.platform = detect_platform()
        self.checks_passed = True
    
    def print_banner(self, emoji: str = "🚀") -> None:
        """Print uniform banner"""
        # For non-Python environments (bash/batch) use simple output
        try:
            print_header(f"{emoji} {self.script_name}")
            print()
        except (ImportError, AttributeError, NameError, TypeError):
            # Fallback for cases when colorama is unavailable
            banner_text = f"{emoji} {self.script_name}"
            print("╔" + "═" * 58 + "╗")
            print("║  " + f"{banner_text:<55}" + "║")
            print("╚" + "═" * 58 + "╝")
            print()
    
    def check_python(self, min_version: Tuple[int, int] = (3, 8)) -> bool:
        """
        Check Python availability and version.
        
        See docs/getting-started.md#if-dependencies-are-missing for dependency installation.
        """
        try:
            version = sys.version_info
            if version.major < min_version[0] or (version.major == min_version[0] and version.minor < min_version[1]):
                try:
                    print_error(f"Python {min_version[0]}.{min_version[1]}+ required, found {version.major}.{version.minor}")
                except (ImportError, AttributeError, NameError):
                    print(f"❌ Python {min_version[0]}.{min_version[1]}+ required, found {version.major}.{version.minor}")
                return False
            try:
                print_success(f"Python {version.major}.{version.minor}.{version.micro}")
            except (ImportError, AttributeError, NameError):
                print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
        except (AttributeError, TypeError, ValueError) as e:
            try:
                print_error(f"Error checking Python: {e}")
            except (ImportError, AttributeError, NameError):
                print(f"❌ Error checking Python: {e}")
            return False
    
    def check_docker(self) -> bool:
        """
        Check Docker availability.
        
        See docs/getting-started.md#if-dependencies-are-missing for dependency installation.
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split(',')[0]
                try:
                    print_success(f"Docker: {version}")
                except (ImportError, AttributeError, NameError, TypeError):
                    print(f"✅ Docker: {version}")
                return True
            else:
                try:
                    print_error("Docker not found")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("❌ Docker not found")
                return False
        except FileNotFoundError:
            try:
                print_error("Docker not installed")
            except (ImportError, AttributeError, NameError, TypeError):
                print("❌ Docker not installed")
            return False
        except subprocess.TimeoutExpired:
            try:
                print_error("Timeout checking Docker")
            except (ImportError, AttributeError, NameError, TypeError):
                print("❌ Timeout checking Docker")
            return False
        except Exception as e:
            try:
                print_error(f"Error checking Docker: {e}")
            except (ImportError, AttributeError, NameError, TypeError):
                print(f"❌ Error checking Docker: {e}")
            return False
    
    def check_docker_daemon(self) -> bool:
        """Check that Docker daemon is running"""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print_success("Docker daemon is running")
                return True
            else:
                print_warning("Docker daemon is not running or unavailable")
                print()
                self._print_docker_start_instructions()
                return False
        except FileNotFoundError:
            print_error("Docker not installed")
            return False
        except subprocess.TimeoutExpired:
            print_warning("Failed to check Docker daemon (timeout)")
            print()
            self._print_docker_start_instructions()
            return False
        except Exception as e:
            print_warning(f"Error checking Docker daemon: {e}")
            print()
            self._print_docker_start_instructions()
            return False
    
    def _print_docker_start_instructions(self) -> None:
        """Print instructions for starting Docker daemon"""
        current_platform = detect_platform()
        
        if current_platform == PlatformType.LINUX:
            print("To start Docker daemon:")
            print()
            print("For rootless Docker (recommended):")
            print()
            print("  If rootless Docker is not initialized:")
            print("    dockerd-rootless-setuptool.sh install")
            print("    # This will initialize and automatically start the daemon")
            print()
            print("  If rootless Docker is already initialized but daemon is not running:")
            print("    systemctl --user start docker")
            print("    systemctl --user enable docker  # Enable auto-start on login")
            print()
            print("  Note: The script may automatically offer to initialize and start")
            print("        rootless Docker when you run ./start.sh")
            print()
            print("For system-wide Docker (requires sudo):")
            print("  sudo systemctl start docker")
            print("  sudo systemctl enable docker  # Enable auto-start on boot")
        elif current_platform == PlatformType.MACOS:
            print("To start Docker daemon:")
            print("  Start Docker Desktop from Applications")
            print("  Or via command line: open -a Docker")
        elif current_platform == PlatformType.WINDOWS:
            print("To start Docker daemon:")
            print("  Start Docker Desktop from Start menu")
            print("  Or check that Docker Desktop is running in system tray")
            print()
            print("If using WSL2:")
            print("  wsl")
            print("  sudo service docker start")
        else:
            print("Please start Docker daemon for your platform")
        print()
    
    def check_docker_compose(self) -> bool:
        """Check docker compose availability"""
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                try:
                    print_success(f"Docker Compose: {version}")
                except (ImportError, AttributeError, NameError, TypeError):
                    print(f"✅ Docker Compose: {version}")
                return True
            else:
                try:
                    print_warning("⚠️  Docker Compose not found (trying docker-compose)")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("⚠️  Docker Compose not found (trying docker-compose)")
                # Fallback to docker-compose
                try:
                    result = subprocess.run(
                        ["docker-compose", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        try:
                            print_success(f"docker-compose: {version}")
                        except (ImportError, AttributeError, NameError, TypeError):
                            print(f"✅ docker-compose: {version}")
                        return True
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                return False
        except FileNotFoundError:
            try:
                print_warning("⚠️  Docker Compose not found")
            except (ImportError, AttributeError, NameError, TypeError):
                print("⚠️  Docker Compose not found")
            return False
        except subprocess.TimeoutExpired:
            try:
                print_warning("⚠️  Timeout checking Docker Compose")
            except (ImportError, AttributeError, NameError, TypeError):
                print("⚠️  Timeout checking Docker Compose")
            return False
        except Exception as e:
            try:
                print_warning(f"⚠️  Error checking Docker Compose: {e}")
            except (ImportError, AttributeError, NameError, TypeError):
                print(f"⚠️  Error checking Docker Compose: {e}")
            return False
    
    def check_env_file(self, required: bool = True) -> bool:
        """Check .env file availability"""
        env_path = os.path.join(self.script_dir, ".env")
        if os.path.exists(env_path):
            try:
                print_success(".env file found")
            except (ImportError, AttributeError, NameError, TypeError):
                print("✅ .env file found")
            return True
        else:
            if required:
                try:
                    print_error(".env file not found!")
                    print_info("Run ./setup.sh to create configuration")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("❌ .env file not found!")
                    print("ℹ️  Run ./setup.sh to create configuration")
                return False
            else:
                try:
                    print_warning(".env file not found (optional for this script)")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("⚠️  .env file not found (optional for this script)")
                return True
    
    def check_config_yaml(self, required: bool = True) -> bool:
        """Check config.yaml availability"""
        config_path = os.path.join(self.script_dir, "config.yaml")
        if os.path.exists(config_path):
            try:
                print_success("config.yaml file found")
            except (ImportError, AttributeError, NameError, TypeError):
                print("✅ config.yaml file found")
            return True
        else:
            if required:
                try:
                    print_error("config.yaml file not found!")
                    print_info("Run ./setup.sh to create configuration")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("❌ config.yaml file not found!")
                    print("ℹ️  Run ./setup.sh to create configuration")
                return False
            else:
                try:
                    print_warning("config.yaml file not found (optional for this script)")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("⚠️  config.yaml file not found (optional for this script)")
                return True
    
    def check_venv(self, auto_create: bool = False) -> bool:
        """Check virtual environment availability"""
        venv_path = os.path.join(self.script_dir, "venv")
        if os.path.exists(venv_path):
            try:
                print_success("Virtual environment found")
            except (ImportError, AttributeError, NameError, TypeError):
                print("✅ Virtual environment found")
            return True
        else:
            if auto_create:
                try:
                    print_warning("Virtual environment not found, creating...")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("⚠️  Virtual environment not found, creating...")
                try:
                    from .core.constants import DOCKER_UP_TIMEOUT
                    subprocess.run([sys.executable, "-m", "venv", "venv"], 
                                 check=True, timeout=DOCKER_UP_TIMEOUT)
                    try:
                        print_success("Virtual environment created")
                    except (ImportError, AttributeError, NameError, TypeError):
                        print("✅ Virtual environment created")
                    return True
                except Exception as e:
                    try:
                        print_error(f"Failed to create virtual environment: {e}")
                    except (ImportError, AttributeError, NameError, TypeError):
                        print(f"❌ Failed to create virtual environment: {e}")
                    return False
            else:
                try:
                    print_warning("Virtual environment not found (optional)")
                except (ImportError, AttributeError, NameError, TypeError):
                    print("⚠️  Virtual environment not found (optional)")
                return True
    
    def check_dependencies(self, deps: List[str]) -> bool:
        """Check Python dependencies availability"""
        missing = []
        for dep in deps:
            try:
                __import__(dep)
                print_success(f"  ✓ {dep}")
            except ImportError:
                missing.append(dep)
                print_warning(f"  ✗ {dep} not found")
        
        if missing:
            print_error(f"Missing dependencies: {', '.join(missing)}")
            print_info("Install them: pip install " + " ".join(missing))
            return False
        return True
    
    def run_standard_checks(self) -> bool:
        """Run standard checks depending on script type"""
        try:
            print_info("🔍 Checking dependencies...")
        except (ImportError, AttributeError, NameError, TypeError):
            print("🔍 Checking dependencies...")
        print()
        
        all_passed = True
        
        # Python check is NOT needed for Python scripts - if script ran, Python is already available
        # Python check should be at bash/batch script level before calling Python
        
        # Docker check for scripts working with containers
        if self.script_type in [ScriptType.START, ScriptType.STOP, ScriptType.MONITORING]:
            try:
                print_info("Docker:")
            except (ImportError, AttributeError, NameError, TypeError):
                print("Docker:")
            if not self.check_docker():
                all_passed = False
            else:
                if not self.check_docker_daemon():
                    all_passed = False
                if not self.check_docker_compose():
                    all_passed = False
            print()
        
        # .env check
        # For START script type, .env is optional - start.sh will handle it interactively
        if self.script_type == ScriptType.START:
            try:
                print_info("Configuration:")
            except (ImportError, AttributeError, NameError, TypeError):
                print("Configuration:")
            # For start.sh, .env is optional - script will prompt user to run setup
            if not self.check_env_file(required=False):
                # Just warn, don't fail - start.sh will handle it
                pass
        elif self.script_type == ScriptType.TEST:
            try:
                print_info("Configuration:")
            except (ImportError, AttributeError, NameError, TypeError):
                print("Configuration:")
            if not self.check_env_file(required=True):
                all_passed = False
            if self.script_type == ScriptType.TEST:
                if not self.check_config_yaml(required=True):
                    all_passed = False
            print()
        
        # Python dependencies for tests
        if self.script_type == ScriptType.TEST:
            try:
                print_info("Python dependencies:")
            except (ImportError, AttributeError, NameError, TypeError):
                print("Python dependencies:")
            deps = ["yaml", "requests"]
            if not self.check_dependencies(deps):
                all_passed = False
            print()
        
        self.checks_passed = all_passed
        return all_passed
    
    def get_summary(self) -> Dict[str, bool]:
        """Get checks summary"""
        return {
            "python": True,  # Python is checked at platform script level
            "docker": self.check_docker() if self.script_type in [ScriptType.START, ScriptType.STOP, ScriptType.MONITORING] else True,
            "env": self.check_env_file(required=False),
            "config": self.check_config_yaml(required=False),
        }


def init_script(script_name: str, script_type: ScriptType, emoji: str = "🚀") -> ScriptInit:
    """
    Initialize script with uniform checks
    
    Args:
        script_name: Script name
        script_type: Script type
        emoji: Emoji for banner
    
    Returns:
        ScriptInit object for further checks
    """
    init = ScriptInit(script_name, script_type)
    init.print_banner(emoji)
    return init
