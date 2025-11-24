"""
Platform detection and utilities
"""

import sys
import platform
from typing import Tuple, Optional
from enum import Enum


class PlatformType(str, Enum):
    """Platform types"""
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


def detect_platform() -> PlatformType:
    """Detect current platform"""
    system = platform.system().lower()
    
    if system == "linux":
        return PlatformType.LINUX
    elif system == "darwin":
        return PlatformType.MACOS
    elif system == "windows":
        return PlatformType.WINDOWS
    else:
        return PlatformType.UNKNOWN


def get_python_command() -> Optional[str]:
    """Get Python command (python3, python, or None)"""
    import shutil
    
    # Try python3 first (most common on Linux/macOS)
    if shutil.which("python3"):
        return "python3"
    
    # Try python (Windows, some Linux)
    if shutil.which("python"):
        # Check version
        import subprocess
        try:
            from .core.constants import SUBPROCESS_TIMEOUT
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            version_str = result.stdout.strip()
            # Extract version number
            version_parts = version_str.split()[-1].split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            if major >= 3 and minor >= 8:
                return "python"
        except (subprocess.CalledProcessError, ValueError, IndexError):
            pass
    
    return None


def get_python_version() -> Optional[Tuple[int, int, int]]:
    """Get Python version as tuple (major, minor, patch)"""
    python_cmd = get_python_command()
    if not python_cmd:
        return None
    
    import subprocess
    try:
        from .core.constants import SUBPROCESS_TIMEOUT
        result = subprocess.run(
            [python_cmd, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=SUBPROCESS_TIMEOUT
        )
        version_str = result.stdout.strip()
        # Extract version number (e.g., "Python 3.11.5")
        version_parts = version_str.split()[-1].split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        patch = int(version_parts[2]) if len(version_parts) > 2 else 0
        return (major, minor, patch)
    except (subprocess.CalledProcessError, ValueError, IndexError):
        return None


def check_python_installed() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if Python is installed
    Returns: (is_installed, python_command, version_string)
    """
    python_cmd = get_python_command()
    if not python_cmd:
        return False, None, None
    
    version = get_python_version()
    if not version:
        return False, python_cmd, None
    
    major, minor, patch = version
    if major < 3 or (major == 3 and minor < 8):
        return False, python_cmd, f"{major}.{minor}.{patch}"
    
    version_str = f"{major}.{minor}.{patch}"
    return True, python_cmd, version_str


def get_python_download_url() -> str:
    """Get Python download URL for current platform"""
    current_platform = detect_platform()
    
    if current_platform == PlatformType.WINDOWS:
        return "https://www.python.org/downloads/windows/"
    elif current_platform == PlatformType.MACOS:
        return "https://www.python.org/downloads/macos/"
    else:
        return "https://www.python.org/downloads/"


def get_docker_install_instructions() -> str:
    """Get Docker installation instructions for current platform"""
    current_platform = detect_platform()
    
    if current_platform == PlatformType.LINUX:
        return """Install Docker:
  Fedora/RHEL: sudo dnf install docker
  Ubuntu/Debian: curl -fsSL https://get.docker.com | sh
  Arch: sudo pacman -S docker

After installation, add user to docker group:
  sudo usermod -aG docker $(whoami)
  newgrp docker"""
    
    elif current_platform == PlatformType.MACOS:
        return """Install Docker Desktop for macOS:
  1. Download: https://www.docker.com/products/docker-desktop
  2. Install .dmg file
  3. Start Docker Desktop from Applications"""
    
    elif current_platform == PlatformType.WINDOWS:
        return """Install Docker Desktop for Windows:
  1. Download: https://www.docker.com/products/docker-desktop
  2. Install Docker Desktop
  3. Start Docker Desktop

Alternative: Use WSL2 with Docker:
  1. Install WSL2: wsl --install
  2. In WSL install Docker: curl -fsSL https://get.docker.com | sh"""
    
    else:
        return "Install Docker for your platform: https://www.docker.com/get-started"

