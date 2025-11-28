"""
System dependency checks and validation.

Cross-platform support for Linux, macOS, Windows.

See docs/getting-started.md#if-dependencies-are-missing for dependency installation.
"""

import os
import shutil
import socket
import subprocess
from typing import Optional, Tuple

from .infrastructure.output import print_error, print_info, print_success, print_warning
from .platform_utils import (
    PlatformType,
    detect_platform,
    get_docker_install_instructions,
)


def check_command(command: str, error_msg: Optional[str] = None) -> bool:
    """Check if command exists in PATH"""
    if shutil.which(command) is None:
        if error_msg:
            print_error(error_msg)
        return False
    return True


def check_docker() -> Tuple[bool, Optional[str]]:
    """Check if Docker is installed and running (cross-platform)"""
    current_platform = detect_platform()

    # Check Docker installation
    if not check_command("docker"):
        print_error("Docker is not installed")
        print()
        print(get_docker_install_instructions())
        print()
        return False, None

    try:
        from .core.constants import DOCKER_TIMEOUT

        version = (
            subprocess.check_output(
                ["docker", "--version"],
                stderr=subprocess.DEVNULL,
                timeout=DOCKER_TIMEOUT,
            )
            .decode()
            .strip()
        )
        print_success(f"Docker installed: {version}")
    except subprocess.CalledProcessError:
        print_error("Failed to get Docker version")
        return False, None

    # Check Docker daemon
    try:
        from .core.constants import DOCKER_TIMEOUT

        subprocess.run(
            ["docker", "ps"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=DOCKER_TIMEOUT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Docker daemon is not running")
        print()

        if current_platform == PlatformType.LINUX:
            print("Start Docker in rootless mode:")
            print("  systemctl --user start docker")
            print("  systemctl --user enable docker")
            print()
            print("Or for system-wide (not recommended):")
            print("  sudo systemctl start docker")
        elif current_platform == PlatformType.MACOS:
            print("Start Docker Desktop from Applications")
            print("Or via command line:")
            print("  open -a Docker")
        elif current_platform == PlatformType.WINDOWS:
            print("Start Docker Desktop from Start menu")
            print("Or check that Docker Desktop is running in system tray")
            print()
            print("If using WSL2:")
            print("  wsl")
            print("  sudo service docker start")
        else:
            print("Start Docker for your platform")
        print()
        return False, None

    # Check rootless mode (only on Linux)
    if current_platform == PlatformType.LINUX:
        try:
            from .core.constants import DOCKER_TIMEOUT

            docker_host = (
                subprocess.check_output(
                    ["docker", "context", "show"],
                    stderr=subprocess.DEVNULL,
                    timeout=DOCKER_TIMEOUT,
                )
                .decode()
                .strip()
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            docker_host = "default"

        docker_host_env = os.environ.get("DOCKER_HOST", "")
        is_rootless = (
            docker_host == "rootless"
            or "/run/user" in docker_host_env
            or os.path.exists(os.path.expanduser("~/.docker/run/docker.sock"))
        )

        if is_rootless:
            print_success("Docker daemon is running (rootless mode) 🔒")
        else:
            print_success("Docker daemon is running")
            print_info("Tip: Consider using rootless Docker for better security")
    else:
        print_success("Docker daemon is running")

    return True, version


def check_docker_compose() -> bool:
    """Check if Docker Compose is available"""
    # Try docker compose (v2)
    try:
        from .core.constants import DOCKER_TIMEOUT

        subprocess.run(
            ["docker", "compose", "version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=DOCKER_TIMEOUT,
        )
        print_success("Docker Compose available (v2)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try docker-compose (v1)
    if check_command("docker-compose"):
        print_success("Docker Compose available (v1)")
        return True

    print_warning("Docker Compose not found")
    print("Usually comes with Docker, but can be installed separately")
    print()
    return False


def check_openssl() -> bool:
    """Check if OpenSSL is installed (cross-platform)"""
    current_platform = detect_platform()

    if not check_command("openssl"):
        print_error("OpenSSL is not installed")
        print()

        if current_platform == PlatformType.LINUX:
            print("Install:")
            print("  Fedora/RHEL: sudo dnf install openssl")
            print("  Ubuntu/Debian: sudo apt install openssl")
            print("  Arch: sudo pacman -S openssl")
        elif current_platform == PlatformType.MACOS:
            print("OpenSSL is usually pre-installed on macOS")
            print("If missing, install via Homebrew:")
            print("  brew install openssl")
        elif current_platform == PlatformType.WINDOWS:
            print("For Windows OpenSSL is not required")
            print("Script will use built-in Python functions")
            print_warning("OpenSSL skipped (not critical for Windows)")
            return True  # Not critical on Windows

        return False

    print_success("OpenSSL available")
    return True


def check_port_available(port: int, service: str = "") -> Tuple[bool, Optional[str]]:
    """
    Check if port is available
    Returns: (is_available, error_message)
    """
    try:
        # Try to bind to the port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", port))
            return True, None
    except OSError as e:
        if e.errno == 98:  # Address already in use
            error_msg = f"Port {port} is already in use"
            if service:
                error_msg += f" (service: {service})"
            return False, error_msg
        return False, str(e)


def check_all_dependencies() -> bool:
    """Check all system dependencies (cross-platform)"""
    current_platform = detect_platform()
    print_info(f"Checking dependencies ({current_platform.value})...")
    print()

    docker_ok, _ = check_docker()
    if not docker_ok:
        return False

    compose_ok = check_docker_compose()
    if not compose_ok:
        return False

    # OpenSSL is optional on Windows
    openssl_ok = check_openssl()
    if not openssl_ok and current_platform != PlatformType.WINDOWS:
        return False

    print()
    return True


# Import os for check_port_available
