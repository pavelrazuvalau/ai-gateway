#!/usr/bin/env python3
"""
Cross-platform Python virtual environment setup (Module Entry Point)
Supports Linux, macOS, and Windows
Run with: python -m src.venv_setup
This is the internal entry point, called by venv.sh
For normal use, prefer: ./venv.sh
"""

import sys
import subprocess
from pathlib import Path

# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Add project root to path so we can import src.*
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.platform_utils import detect_platform, check_python_installed, PlatformType
from src.utils import print_success, print_error, print_info, print_warning, Colors


def main():
    """Main function for venv setup"""
    print(f"{Colors.BLUE}🔧 Setting up Python virtual environment...{Colors.RESET}")
    print()
    
    current_platform = detect_platform()
    print_info(f"Platform: {current_platform.value}")
    print()
    
    # Check Python
    is_installed, python_cmd, version = check_python_installed()
    
    if not is_installed:
        print_error("Python 3.8+ not found")
        print()
        
        if current_platform == PlatformType.WINDOWS:
            print("For Windows:")
            print("  1. Download Python: https://www.python.org/downloads/windows/")
            print("  2. Install Python 3.8+ (check 'Add Python to PATH')")
            print("  3. Restart terminal/command prompt")
        elif current_platform == PlatformType.MACOS:
            print("For macOS:")
            print("  brew install python@3.11")
            print("  or download: https://www.python.org/downloads/macos/")
        else:
            print("For Linux:")
            print("  sudo dnf/apt/pacman install python3 python3-pip python3-venv")
        
        sys.exit(1)
    
    print_success(f"Python {version} found ({python_cmd})")
    print()
    
    # Determine venv directory
    if current_platform == PlatformType.WINDOWS:
        VENV_DIR = PROJECT_ROOT / "venv"
        activate_script = VENV_DIR / "Scripts" / "activate.bat"
        python_exe = VENV_DIR / "Scripts" / "python.exe"
    else:
        VENV_DIR = PROJECT_ROOT / "venv"
        activate_script = VENV_DIR / "bin" / "activate"
        python_exe = VENV_DIR / "bin" / "python"
    
    # Create venv if not exists
    if not VENV_DIR.exists():
        print_info("📦 Creating virtual environment...")
        try:
            result = subprocess.run(
                [python_cmd, "-m", "venv", str(VENV_DIR)],
                check=True,
                capture_output=True,
                text=True
            )
            print_success("Virtual environment created")
        except subprocess.CalledProcessError as e:
            print_error("Failed to create virtual environment")
            if e.stderr and "ensurepip" in e.stderr.lower():
                print()
                print_warning("The virtual environment was not created because ensurepip is not available.")
                print()
                if current_platform == PlatformType.LINUX:
                    print_info("On Debian/Ubuntu systems, install the python3-venv package:")
                    print("  sudo apt install python3-venv")
                elif current_platform == PlatformType.MACOS:
                    print_info("On macOS, ensure Python was installed with pip support")
                else:
                    print_info("Install the python3-venv package for your distribution")
            else:
                print_error(f"Error: {e}")
                if e.stderr:
                    print(e.stderr)
            sys.exit(1)
    else:
        print_success("Virtual environment already exists")
    
    print()
    
    # Install dependencies
    print_info("📦 Installing dependencies...")
    
    # Determine pip command
    if current_platform == PlatformType.WINDOWS:
        pip_cmd = python_exe
    else:
        pip_cmd = str(python_exe)
    
    try:
        # Upgrade pip
        subprocess.run(
            [python_exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
            check=True
        )
        
        # Install requirements
        requirements_file = PROJECT_ROOT / "requirements.txt"
        if requirements_file.exists():
            subprocess.run(
                [python_exe, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True
            )
        else:
            print_warning("requirements.txt not found, installing basic dependencies")
            subprocess.run(
                [python_exe, "-m", "pip", "install", "colorama", "pyyaml"],
                check=True
            )
        
        print_success("Dependencies installed")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        sys.exit(1)
    
    print()
    print_success("✅ Virtual environment ready!")
    print()
    print_info("To activate run:")
    
    if current_platform == PlatformType.WINDOWS:
        print(f"  {VENV_DIR}\\Scripts\\activate")
        print("  or")
        print(f"  {VENV_DIR}\\Scripts\\activate.bat")
    else:
        print(f"  source {VENV_DIR}/bin/activate")
    
    print()
    print_info("Or use ./setup.sh and ./start.sh scripts (they activate venv automatically)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

