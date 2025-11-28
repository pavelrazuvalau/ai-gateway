"""
Formatted output utilities for console messages.

This module provides formatted output functions that replace the deprecated
utils.print_* functions. Uses infrastructure.logger under the hood while
maintaining compatibility with the existing API (emojis, colors).
"""

import sys
from typing import Optional

try:
    from colorama import Fore, Style, init

    # Initialize colorama for cross-platform color support
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback when colorama is not available
    COLORAMA_AVAILABLE = False

    # Create dummy classes for Fore and Style
    # Type ignore needed because mypy sees Fore/Style from import above
    class Fore:  # type: ignore[no-redef]
        RED = ""
        GREEN = ""
        LIGHTGREEN_EX = ""
        YELLOW = ""
        LIGHTYELLOW_EX = ""
        BLUE = ""
        LIGHTCYAN_EX = ""
        CYAN = ""
        MAGENTA = ""

    class Style:  # type: ignore[no-redef]
        RESET_ALL = ""
        BRIGHT = ""

from .logger import get_logger

logger = get_logger(__name__)


class Colors:
    """Color constants for terminal output"""

    RED = Fore.RED if COLORAMA_AVAILABLE else "\033[0;31m"
    GREEN = Fore.GREEN if COLORAMA_AVAILABLE else "\033[1;32m"
    YELLOW = Fore.YELLOW if COLORAMA_AVAILABLE else "\033[1;33m"
    BLUE = Fore.BLUE if COLORAMA_AVAILABLE else "\033[1;34m"
    CYAN = Fore.CYAN if COLORAMA_AVAILABLE else "\033[1;36m"
    RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else "\033[0m"


def print_error(text: str) -> None:
    """
    Print error message in red.

    Args:
        text: Error message to print
    """
    message = f"❌ {text}"
    if sys.stdout.isatty():
        print(f"{Colors.RED}{message}{Colors.RESET}")
    else:
        print(message)
    logger.error(text)


def print_success(text: str) -> None:
    """
    Print success message in green.

    Args:
        text: Success message to print
    """
    message = f"✅ {text}"
    if sys.stdout.isatty():
        print(f"{Colors.GREEN}{message}{Colors.RESET}")
    else:
        print(message)
    logger.info(text)


def print_warning(text: str) -> None:
    """
    Print warning message in yellow.

    Args:
        text: Warning message to print
    """
    message = f"⚠️  {text}"
    if sys.stdout.isatty():
        print(f"{Colors.YELLOW}{message}{Colors.RESET}")
    else:
        print(message)
    logger.warning(text)


def print_info(text: str) -> None:
    """
    Print info message in blue.

    Args:
        text: Info message to print
    """
    message = f"ℹ️  {text}"
    if sys.stdout.isatty():
        print(f"{Colors.BLUE}{message}{Colors.RESET}")
    else:
        print(message)
    logger.info(text)


def print_step(text: str) -> None:
    """
    Print step message.

    Args:
        text: Step message to print
    """
    message = f"📋 {text}"
    if sys.stdout.isatty():
        print(f"{Colors.CYAN}{message}{Colors.RESET}")
    else:
        print(message)
    logger.info(text)


def print_header(text: str) -> None:
    """
    Print header with banner.

    Args:
        text: Header text to print
    """
    banner_text = str(text)
    if sys.stdout.isatty():
        print(f"{Colors.BLUE}╔{'═' * 58}╗{Colors.RESET}")
        print(f"{Colors.BLUE}║  {banner_text:<55}║{Colors.RESET}")
        print(f"{Colors.BLUE}╚{'═' * 58}╝{Colors.RESET}")
    else:
        print(f"{'=' * 60}")
        print(f"  {banner_text}")
        print(f"{'=' * 60}")
    logger.info(f"=== {banner_text} ===")


def is_non_interactive() -> bool:
    """
    Check if running in non-interactive mode.

    Returns:
        True if NON_INTERACTIVE env var is set to "1"
    """
    import os
    return os.environ.get("NON_INTERACTIVE", "0") == "1"


def ask_yes_no(prompt: str, default: bool = True, non_interactive: Optional[bool] = None) -> bool:
    """
    Ask user yes/no question.

    Args:
        prompt: Question to ask
        default: Default value if user just presses Enter
        non_interactive: If True, skip prompt and return default. If None, check NON_INTERACTIVE env var.

    Returns:
        True if yes, False if no
    """
    # Check non-interactive mode
    if non_interactive is None:
        non_interactive = is_non_interactive()

    if non_interactive:
        return default

    default_text = "[Y/n]" if default else "[y/N]"
    try:
        response = input(f"{prompt} {default_text}: ").strip().lower()

        if not response:
            return default

        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return not default  # Return opposite of default on interrupt


def print_access_urls(
    local_ip: str,
    use_nginx: bool,
    nginx_http_port: Optional[int],
    webui_port: str,
    litellm_external_port: Optional[str],
) -> None:
    """
    Print access URLs for services.

    Args:
        local_ip: Local network IP address
        use_nginx: Whether nginx is used
        nginx_http_port: Nginx HTTP port (if using nginx)
        webui_port: WebUI port (if not using nginx)
        litellm_external_port: LiteLLM external port
    """
    print()
    print_info("🌐 Access URLs (local network):")
    print()

    if use_nginx and nginx_http_port:
        print(f"  • Open WebUI: http://{local_ip}:{nginx_http_port}")

        if litellm_external_port:
            print(
                f"  • LiteLLM UI: http://{local_ip}:{litellm_external_port}/ui"
            )
        else:
            print_warning(
                "  • LiteLLM UI: port not configured, check docker-compose.override.yml"
            )
        print()
        print_info(
            "ℹ️  Note: LiteLLM UI accessible only from local/VPN network (security)"
        )
        print()
        print_info(
            "💡 Note: Configure SSL/HTTPS via your own nginx container"
        )
    else:
        print(f"  • Open WebUI: http://{local_ip}:{webui_port}")
        if litellm_external_port:
            print(f"  • LiteLLM API: http://{local_ip}:{litellm_external_port}")
            print(
                f"  • LiteLLM Admin UI: http://{local_ip}:{litellm_external_port}/ui"
            )

    print()


def print_api_info(
    local_ip: str,
    nginx_http_port: Optional[int],
    virtual_key: Optional[str],
    use_nginx: bool,
) -> None:
    """
    Print API access information.

    Args:
        local_ip: Local network IP address
        nginx_http_port: Nginx HTTP port (if using nginx)
        virtual_key: Virtual Key for API access
        use_nginx: Whether nginx is used
    """
    if not use_nginx or not nginx_http_port:
        return

    api_url = f"http://{local_ip}:{nginx_http_port}/api/litellm/v1"

    if virtual_key:
        print(f"  • LiteLLM API: {api_url}")
        print(f"    API Key: {virtual_key}")
        print()
        print_info(
            "💡 Use this API Key for external clients (agents, scripts, etc.)"
        )
        print_info(
            "   ✅ Open WebUI is configured to use Virtual Key automatically"
        )
        print()
    else:
        print(f"  • LiteLLM API: {api_url}")
        print(
            "    API Key: Use Master Key or run ./virtual-key.sh to create Virtual Key"
        )
        print()
        print_warning(
            "⚠️  Virtual Key not configured - Open WebUI uses Master Key"
        )
        print_info(
            "   Run ./virtual-key.sh to create Virtual Key for better security"
        )
        print()


def print_status_commands() -> None:
    """Print commands for checking status and viewing logs"""
    print()
    print_info("📊 Check status:")
    print("  docker compose ps")
    print()
    print_info("📝 View logs:")
    print("  docker compose logs -f")
    print()

