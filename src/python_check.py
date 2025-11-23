"""
Python installation check and setup
"""

import sys
import subprocess
import webbrowser
from typing import Tuple, Optional
from .platform_utils import (
    detect_platform, check_python_installed, PlatformType
)
from .utils import print_error, print_warning, print_info, print_success, Colors


def check_python() -> Tuple[bool, Optional[str]]:
    """
    Check if Python 3.8+ is installed
    Returns: (is_ok, python_command)
    """
    is_installed, python_cmd, version = check_python_installed()
    
    if not is_installed:
        current_platform = detect_platform()
        
        print_error("Python 3.8+ not found")
        print()
        
        if python_cmd and version:
            print_warning(f"Found Python {version}, requires 3.8+")
            print()
        
        print_info("Installing Python:")
        print()
        
        if current_platform == PlatformType.WINDOWS:
            print("For Windows:")
            print("  1. Download Python: https://www.python.org/downloads/windows/")
            print("  2. Install Python 3.8+ (check 'Add Python to PATH')")
            print("  3. Restart terminal/command prompt")
            print()
            print("Or use Microsoft Store:")
            print("  winget install Python.Python.3.11")
            print()
            
            # Try to open browser
            try:
                open_browser = input("Open Python download page in browser? [Y/n]: ").strip().lower()
                if open_browser != 'n':
                    webbrowser.open("https://www.python.org/downloads/windows/")
            except Exception:
                pass
        
        elif current_platform == PlatformType.MACOS:
            print("For macOS:")
            print()
            print("  ⚠️  Python is NOT pre-installed on modern macOS versions!")
            print()
            print("  Installation options:")
            print()
            print("  1. Via Homebrew (recommended):")
            print("     brew install python@3.11")
            print()
            print("  2. Download from python.org:")
            print("     https://www.python.org/downloads/macos/")
            print()
            print("  3. Xcode Command Line Tools (may be old version):")
            print("     xcode-select --install")
            print()
            
            # Check for Homebrew
            try:
                from .core.constants import SUBPROCESS_TIMEOUT
                subprocess.run(["brew", "--version"], 
                             capture_output=True, check=True,
                             timeout=SUBPROCESS_TIMEOUT)
                print_info("✅ Homebrew found. Can install: brew install python@3.11")
                print()
                install_brew = input("Install Python via Homebrew now? [y/N]: ").strip().lower()
                if install_brew == 'y':
                    try:
                        from .core.constants import DOCKER_UP_TIMEOUT
                        subprocess.run(["brew", "install", "python@3.11"], 
                                     check=True, timeout=DOCKER_UP_TIMEOUT)
                        print_success("Python installed via Homebrew!")
                        # Re-check
                        is_ok, python_cmd = check_python()
                        if is_ok:
                            return True, python_cmd
                    except subprocess.CalledProcessError as e:
                        print_error(f"Failed to install Python: {e}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print_warning("Homebrew not found. Install: https://brew.sh")
                print()
                print("Or download Python manually: https://www.python.org/downloads/macos/")
        
        else:  # Linux
            print("For Linux:")
            print("  Fedora/RHEL: sudo dnf install python3 python3-pip python3-venv")
            print("  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv")
            print("  Arch: sudo pacman -S python python-pip")
            print()
        
        return False, None
    
    print_success(f"Python {version} found ({python_cmd})")
    return True, python_cmd


def ensure_python() -> Optional[str]:
    """
    Ensure Python is installed, prompt for installation if not
    Returns: python_command or None
    """
    is_ok, python_cmd = check_python()
    
    if is_ok:
        return python_cmd
    
    print()
    print_warning("Python is required for setup to work")
    print()
    
    retry = input("Retry check after installing Python? [Y/n]: ").strip().lower()
    if retry == 'n':
        return None
    
    # Re-check
    is_ok, python_cmd = check_python()
    if is_ok:
        return python_cmd
    
    return None

