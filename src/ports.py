"""
Port management and configuration
"""

from typing import Tuple, Optional, Dict, Any
from .utils import print_success, print_warning, print_error, print_info, Colors
from .checks import check_port_available
from .core.constants import (
    DEFAULT_LITELLM_PORT, DEFAULT_WEBUI_PORT, DEFAULT_POSTGRES_PORT,
    DEFAULT_WEBUI_INTERNAL_PORT, DEFAULT_NGINX_HTTP_PORT, DEFAULT_NGINX_HTTPS_PORT,
    MIN_PORT, MAX_PORT, HIGH_PORT_MIN, HIGH_PORT_MAX
)
import random
import os
import subprocess
from .core.exceptions import PortError, ValidationError


def is_rootless_docker() -> bool:
    """
    Check if Docker is running in rootless mode
    Returns True if rootless, False otherwise
    
    Note: Since the script prevents running as root, if we're not root,
    Docker must be rootless (script enforces this).
    """
    try:
        from .platform_utils import detect_platform, PlatformType
        current_platform = detect_platform()
        
        # Only check on Linux
        if current_platform != PlatformType.LINUX:
            return False
        
        # If script is not running as root, Docker must be rootless
        # (script prevents root execution)
        if os.geteuid() != 0:
            return True
        
        # If we somehow got here as root (shouldn't happen due to check_root),
        # check docker context and indicators
        try:
            from .core.constants import DOCKER_TIMEOUT
            docker_host = subprocess.check_output(
                ["docker", "context", "show"],
                stderr=subprocess.DEVNULL,
                timeout=DOCKER_TIMEOUT
            ).decode().strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            docker_host = "default"
        
        # Check environment variable
        docker_host_env = os.environ.get("DOCKER_HOST", "")
        
        # Check for rootless indicators
        is_rootless = (
            docker_host == "rootless" or 
            "/run/user" in docker_host_env or
            os.path.exists(os.path.expanduser("~/.docker/run/docker.sock"))
        )
        
        return is_rootless
    except Exception:
        # If check fails, assume rootless if not root (safer default)
        return os.geteuid() != 0


def generate_random_high_port(used_ports: Optional[Dict[int, str]] = None, max_attempts: int = 100) -> int:
    """
    Generate a random port from high port range (49152-65535) for security
    
    Args:
        used_ports: Dictionary of already used ports to avoid conflicts
        max_attempts: Maximum attempts to find available port
    
    Returns:
        Random port number from high range
    
    Raises:
        PortError: If no available port found after max_attempts
    """
    for _ in range(max_attempts):
        port = random.randint(HIGH_PORT_MIN, HIGH_PORT_MAX)
        if used_ports is None or port not in used_ports:
            # Check if port is actually available
            from .checks import check_port_available
            is_available, _ = check_port_available(port, "random")
            if is_available:
                return port
    raise PortError(f"Could not find available port in range {HIGH_PORT_MIN}-{HIGH_PORT_MAX} after {max_attempts} attempts")


def select_port_interactive(
    service_name: str,
    default_port: int,
    description: str,
    is_internal: bool = False,
    used_ports: Optional[Dict[int, str]] = None,
    default_ports: Optional[Dict[int, str]] = None
) -> int:
    """
    Interactive port selection
    
    Args:
        service_name: Name of the service
        default_port: Default port number
        description: Description of the port usage
        is_internal: Whether this is an internal port
        used_ports: Dictionary of already used ports
        default_ports: Dictionary of default ports for conflict checking
    
    Returns:
        Selected port number
    
    Raises:
        ValidationError: If port is out of valid range
        PortError: If port is already in use
    """
    # Validate default port (allow ports 80 and 443 for nginx even if < 1024)
    if not (MIN_PORT <= default_port <= MAX_PORT) and default_port not in (80, 443):
        raise ValidationError(f"Default port {default_port} is out of valid range ({MIN_PORT}-{MAX_PORT})")
    # Warn about rootless Docker restrictions if default port is privileged
    if default_port < 1024 and is_rootless_docker() and not is_internal:
        print_warning(f"Default port {default_port} is privileged (< 1024)")
        print_info("Rootless Docker cannot use privileged ports without special configuration")
        print_info("Consider using option [4] for random high port")
        print()
    
    print(f"{Colors.YELLOW}{service_name}:{Colors.RESET}")
    
    if is_internal:
        print(f"  {Colors.BLUE}[1] Default port {default_port}{Colors.RESET} (recommended)")
        print(f"  {Colors.BLUE}[2] Specify custom port{Colors.RESET} (for security)")
        print(f"  {Colors.BLUE}[3] Random high port{Colors.RESET} ({HIGH_PORT_MIN}-{HIGH_PORT_MAX}, enhanced security)")
        print()
        
        while True:
            choice = input("Select option [1-3]: ").strip()
            
            if choice == "1":
                port = default_port
            elif choice == "2":
                while True:
                    try:
                        port = int(input("Enter port number (1024-65535, or 80/443 for nginx): "))
                        if (1024 <= port <= 65535) or port in (80, 443):
                            # Check rootless Docker restrictions for privileged ports
                            if port < 1024 and port not in (80, 443):
                                if is_rootless_docker():
                                    print_error(f"Port {port} is privileged (< 1024)")
                                    print_warning("Rootless Docker cannot use privileged ports without special configuration")
                                    print_info("Please use a port >= 1024, or select option [4] for random high port")
                                    continue
                            
                            # Check conflicts with already selected ports
                            if used_ports and port in used_ports:
                                print_warning(f"Port {port} is already used for {used_ports[port]}.")
                                print_info("Select another port.")
                                continue
                            # Check conflicts with default standard ports
                            if default_ports and port in default_ports:
                                print_warning("Port conflict!")
                                print_warning(f"Port {port} is standard for {default_ports[port]}.")
                                print_info("This may cause issues on startup.")
                                confirm = input("Use this port anyway? [y/N]: ").strip().lower()
                                if confirm != 'y':
                                    print_info("Select another port.")
                                    continue
                            print_success(f"Using port {port}")
                            if used_ports is not None:
                                used_ports[port] = service_name
                            return port
                        else:
                            print_error("Invalid port. Enter a number from 1024 to 65535, or 80/443 for nginx")
                    except ValueError:
                        print_error("Invalid format. Enter a number")
                continue
            elif choice == "3":
                # Generate random high port
                try:
                    port = generate_random_high_port(used_ports=used_ports)
                    print_success(f"Generated random high port: {port} (range: {HIGH_PORT_MIN}-{HIGH_PORT_MAX})")
                    if used_ports is not None:
                        used_ports[port] = service_name
                    return port
                except PortError as e:
                    print_error(str(e))
                    print_info("Try selecting a custom port manually")
                    continue
            else:
                print_error("Invalid choice. Enter 1, 2, or 3")
                continue
            
            # Check conflicts with already selected ports
            if used_ports and port in used_ports:
                print_warning(f"Port {port} is already used for {used_ports[port]}.")
                print_info("Select another port.")
                continue
            
            # Check conflicts with default standard ports
            if default_ports and port in default_ports:
                print_warning("Port conflict!")
                print_warning(f"Port {port} is standard for {default_ports[port]}.")
                print_info("This may cause issues on startup.")
                confirm = input("Use this port anyway? [y/N]: ").strip().lower()
                if confirm != 'y':
                    print_info("Select another port.")
                    continue
            
            print_success(f"Using default port {port}")
            if used_ports is not None:
                used_ports[port] = service_name
            return port
    else:
        print(f"  {Colors.BLUE}[1] Default port {default_port}{Colors.RESET} (HTTP)")
        print(f"  {Colors.BLUE}[2] Port {DEFAULT_NGINX_HTTPS_PORT}{Colors.RESET} (HTTPS, SSL certificate required)")
        print(f"  {Colors.BLUE}[3] Specify custom port{Colors.RESET}")
        print(f"  {Colors.BLUE}[4] Random high port{Colors.RESET} ({HIGH_PORT_MIN}-{HIGH_PORT_MAX}, enhanced security)")
        print()
        
        while True:
            choice = input("Select option [1-4]: ").strip()
            
            selected_port = None
            if choice == "1":
                selected_port = default_port
            elif choice == "2":
                selected_port = DEFAULT_NGINX_HTTPS_PORT
            elif choice == "3":
                while True:
                    try:
                        port = int(input("Enter port number (1024-65535, or 80/443 for nginx): "))
                        if (1024 <= port <= 65535) or port in (80, 443):
                            # Check rootless Docker restrictions for privileged ports
                            if port < 1024 and port not in (80, 443):
                                if is_rootless_docker():
                                    print_error(f"Port {port} is privileged (< 1024)")
                                    print_warning("Rootless Docker cannot use privileged ports without special configuration")
                                    print_info("Please use a port >= 1024, or select option [4] for random high port")
                                    continue
                            
                            # Check conflicts with already selected ports
                            if used_ports and port in used_ports:
                                print_warning(f"Port {port} is already used for {used_ports[port]}.")
                                print_info("Select another port.")
                                continue
                            # Check conflicts with default standard ports
                            if default_ports and port in default_ports:
                                print_warning("Port conflict!")
                                print_warning(f"Port {port} is standard for {default_ports[port]}.")
                                print_info("This may cause issues on startup.")
                                confirm = input("Use this port anyway? [y/N]: ").strip().lower()
                                if confirm != 'y':
                                    print_info("Select another port.")
                                    continue
                            print_success(f"Using port {port}")
                            if used_ports is not None:
                                used_ports[port] = service_name
                            return port
                        else:
                            print_error("Invalid port. Enter a number from 1024 to 65535, or 80/443 for nginx")
                            print_info(f"Or select option [4] for random high port ({HIGH_PORT_MIN}-{HIGH_PORT_MAX})")
                    except ValueError:
                        print_error("Invalid format. Enter a number")
                        print_info(f"Or select option [4] for random high port ({HIGH_PORT_MIN}-{HIGH_PORT_MAX})")
                        retry = input("Try again? [Y/n] or type '4' for random port: ").strip().lower()
                        if retry == '4':
                            # Switch to random port option
                            try:
                                port = generate_random_high_port(used_ports=used_ports)
                                print_success(f"Generated random high port: {port} (range: {HIGH_PORT_MIN}-{HIGH_PORT_MAX})")
                                if used_ports is not None:
                                    used_ports[port] = service_name
                                return port
                            except PortError as e:
                                print_error(str(e))
                                print_info("Try selecting a custom port manually")
                                continue
                        elif retry == 'n':
                            # Return to main menu
                            break
                continue
            elif choice == "4":
                # Generate random high port
                try:
                    port = generate_random_high_port(used_ports=used_ports)
                    print_success(f"Generated random high port: {port} (range: {HIGH_PORT_MIN}-{HIGH_PORT_MAX})")
                    if used_ports is not None:
                        used_ports[port] = service_name
                    return port
                except PortError as e:
                    print_error(str(e))
                    print_info("Try selecting a custom port manually")
                    continue
            else:
                print_error("Invalid choice. Enter 1, 2, 3, or 4")
                continue
            
            # Check conflicts with already selected ports
            if used_ports and selected_port in used_ports:
                print_warning(f"Port {selected_port} is already used for {used_ports[selected_port]}.")
                print_info("Select another port.")
                continue
            
            # Check conflicts with default standard ports (except HTTPS port)
            if choice != "2" and default_ports and selected_port in default_ports:
                print_warning("Port conflict!")
                print_warning(f"Port {selected_port} is standard for {default_ports[selected_port]}.")
                print_info("This may cause issues on startup.")
                confirm = input("Use this port anyway? [y/N]: ").strip().lower()
                if confirm != 'y':
                    print_info("Select another port.")
                    continue
            
            if choice == "2":
                print_success(f"Using port {DEFAULT_NGINX_HTTPS_PORT} (HTTPS)")
                print_warning("Don't forget to configure SSL certificate!")
            else:
                print_success(f"Using default port {selected_port}")
            
            if used_ports is not None:
                used_ports[selected_port] = service_name
            return selected_port


def configure_ports() -> Dict[str, Any]:
    """
    Configure all ports (internal and external)
    Returns dict with port configuration
    """
    from .utils import print_header, Colors
    
    print_header("🔌 Port Configuration")
    print()
    
    # Check rootless Docker and warn about port restrictions
    if is_rootless_docker():
        print_warning("Rootless Docker detected 🔒")
        print_info("Rootless Docker cannot use privileged ports (< 1024) without special configuration")
        print_info("High ports (49152-65535) are recommended for security")
        print()
    
    print_info("Port configuration for enhanced security:")
    print(f"{Colors.BLUE}Internal ports{Colors.RESET} - only for container-to-container communication")
    print(f"{Colors.BLUE}External port{Colors.RESET} - only nginx (reverse proxy)")
    print()
    
    host_ports_in_use: Dict[int, str] = {}
    internal_ports_in_use: Dict[int, str] = {}
    
    # First ask about nginx
    print_info("Nginx configuration:")
    print("  Nginx is used as reverse proxy (recommended)")
    print("  Without nginx: services are available on separate ports")
    print()
    use_nginx = input("Use nginx (reverse proxy)? [Y/n]: ").strip().lower()
    use_nginx = use_nginx != 'n'  # Default is 'y'
    
    # Nginx configuration (if selected)
    # Simplified: only HTTP, no SSL/vhost configuration
    # Users can configure their own nginx with SSL on separate container
    # Port will be configured together with other ports below
    nginx_http_port = None
    nginx_port = None
    
    if use_nginx:
        print_success("Nginx will be used as reverse proxy")
        print_info("Note: SSL/HTTPS configuration should be done via your own nginx container")
        print_info("This setup provides basic HTTP reverse proxy only")
        print_info("Nginx port will be configured together with other ports")
        print()
    
    # Default standard ports (for conflict checking)
    # Depends on whether nginx is used
    if use_nginx:
        # With nginx: Open WebUI has no external port, only LiteLLM UI
        default_ports = {
            DEFAULT_LITELLM_PORT: "LiteLLM (API and UI)",
            DEFAULT_WEBUI_INTERNAL_PORT: "Open WebUI (internal)",
            DEFAULT_POSTGRES_PORT: "PostgreSQL",
        }
    else:
        # Without nginx: both services have external ports
        default_ports = {
            DEFAULT_LITELLM_PORT: "LiteLLM (API and UI)",
            DEFAULT_WEBUI_PORT: "Open WebUI (external)",
            DEFAULT_WEBUI_INTERNAL_PORT: "Open WebUI (internal)",
            DEFAULT_POSTGRES_PORT: "PostgreSQL",
        }
    
    # Now ask about all ports (including nginx if selected)
    print()
    print(f"{Colors.BLUE}{'═' * 59}{Colors.RESET}")
    print(f"{Colors.BLUE}Port Configuration:{Colors.RESET}")
    print()
    if use_nginx:
        print_info("Configure ports for nginx and other services:")
        print_info("Nginx will use random high port (rootless Docker requirement)")
    else:
        print_info("Configure ports for all services:")
    print()
    print(f"{Colors.BLUE}[1] Use default ports{Colors.RESET} (recommended)")
    print(f"{Colors.BLUE}[2] Configure ports manually{Colors.RESET} (for customization)")
    print(f"{Colors.BLUE}[3] Use random high ports{Colors.RESET} ({HIGH_PORT_MIN}-{HIGH_PORT_MAX}, enhanced security)")
    print()
    print_info("Random high ports make services harder to discover by port scanners")
    if use_nginx:
        print_info("Note: Nginx will always use random high port (rootless Docker)")
    print()
    
    while True:
        choice = input("Select option [1-3]: ").strip()
        if choice == "1":
            default_conflicts = []
            def check_default_port(port: int, service_name: str) -> None:
                owner = host_ports_in_use.get(port)
                if owner:
                    default_conflicts.append((service_name, port, owner))
            
            if use_nginx:
                check_default_port(DEFAULT_LITELLM_PORT, "LiteLLM UI (direct access)")
            else:
                check_default_port(DEFAULT_LITELLM_PORT, "LiteLLM (external)")
                check_default_port(DEFAULT_WEBUI_PORT, "Open WebUI (external)")
            
            if default_conflicts:
                print_warning("Port conflicts detected with default values:")
                for service_name, port, owner in default_conflicts:
                    print_warning(f"  • {service_name} cannot use port {port}, it's already in use: {owner}")
                print_info("Select manual configuration and set ports manually.")
                choice = "2"
                continue
            
            print_success("Using default ports")
            print()
            
            # Configure nginx port if nginx is used
            # Always use random high port for nginx (rootless Docker requirement)
            if use_nginx:
                nginx_port = generate_random_high_port(used_ports=host_ports_in_use)
                host_ports_in_use[nginx_port] = "Nginx HTTP"
                nginx_http_port = nginx_port
                print_success(f"Using random high port for nginx: {nginx_port} (rootless Docker standard)")
            
            if use_nginx:
                host_ports_in_use[DEFAULT_LITELLM_PORT] = "LiteLLM UI (direct access)"
            else:
                host_ports_in_use[DEFAULT_LITELLM_PORT] = "LiteLLM (external)"
                host_ports_in_use[DEFAULT_WEBUI_PORT] = "Open WebUI (external)"
            
            # Default ports
            return {
                "postgres_port": DEFAULT_POSTGRES_PORT,
                "litellm_internal_port": DEFAULT_LITELLM_PORT,
                "webui_internal_port": DEFAULT_WEBUI_INTERNAL_PORT,
                "use_nginx": use_nginx,
                "use_ssl": False,
                "ssl_domain": None,
                "nginx_http_port": nginx_http_port if use_nginx else None,
                "nginx_https_port": None,
                "nginx_port": nginx_port if use_nginx else None,
                "litellm_external_port": DEFAULT_LITELLM_PORT,
                "webui_external_port": DEFAULT_WEBUI_PORT if not use_nginx else None,
            }
        elif choice == "2":
            break
        elif choice == "3":
            # Generate random high ports for all services (including nginx)
            print()
            print_success("Generating random high ports for all services...")
            print_info(f"Port range: {HIGH_PORT_MIN}-{HIGH_PORT_MAX} (enhanced security)")
            print()
            
            # Generate nginx port if nginx is used
            if use_nginx:
                nginx_port = generate_random_high_port(used_ports=host_ports_in_use)
                host_ports_in_use[nginx_port] = "Nginx HTTP"
                nginx_http_port = nginx_port
                print_success(f"Generated random high port for nginx: {nginx_port}")
            
            # Generate ports for all services
            generated_ports = {}
            
            # External ports
            if use_nginx:
                # With nginx: LiteLLM API available through nginx
                # LiteLLM UI needs separate external port for local network access (configuration)
                litellm_external_port = generate_random_high_port(used_ports=host_ports_in_use)
                host_ports_in_use[litellm_external_port] = "LiteLLM UI (direct access, local network)"
                generated_ports['litellm_external_port'] = litellm_external_port
                webui_external_port = None
            else:
                litellm_external_port = generate_random_high_port(used_ports=host_ports_in_use)
                host_ports_in_use[litellm_external_port] = "LiteLLM (external)"
                generated_ports['litellm_external_port'] = litellm_external_port
                
                webui_external_port = generate_random_high_port(used_ports=host_ports_in_use)
                host_ports_in_use[webui_external_port] = "Open WebUI (external)"
                generated_ports['webui_external_port'] = webui_external_port
            
            # Internal ports
            # When using nginx, internal ports should be standard (not random)
            # They're only used for container-to-container communication
            if use_nginx:
                litellm_internal_port = DEFAULT_LITELLM_PORT
                postgres_port = DEFAULT_POSTGRES_PORT
                webui_internal_port = DEFAULT_WEBUI_INTERNAL_PORT
            else:
                litellm_internal_port = generate_random_high_port(used_ports=internal_ports_in_use)
                postgres_port = generate_random_high_port(used_ports=internal_ports_in_use)
                webui_internal_port = generate_random_high_port(used_ports=internal_ports_in_use)
            
            internal_ports_in_use[litellm_internal_port] = "LiteLLM (internal)"
            generated_ports['litellm_internal_port'] = litellm_internal_port
            
            internal_ports_in_use[postgres_port] = "PostgreSQL"
            generated_ports['postgres_port'] = postgres_port
            
            internal_ports_in_use[webui_internal_port] = "Open WebUI (internal)"
            generated_ports['webui_internal_port'] = webui_internal_port
            
            # Display generated ports
            print_success("Generated ports:")
            if use_nginx:
                print(f"  • Nginx HTTP: {nginx_http_port}")
                print(f"  • LiteLLM API: available through nginx at /api/litellm/")
                print(f"  • LiteLLM UI (direct): {litellm_external_port} (local network access)")
                print(f"  • Open WebUI: available through nginx at /")
            else:
                print(f"  • LiteLLM (external): {litellm_external_port}")
                print(f"  • Open WebUI (external): {webui_external_port}")
            print(f"  • LiteLLM (internal): {litellm_internal_port}")
            print(f"  • PostgreSQL (internal): {postgres_port}")
            print(f"  • Open WebUI (internal): {webui_internal_port}")
            print()
            
            return {
                "postgres_port": postgres_port,
                "litellm_internal_port": litellm_internal_port,
                "webui_internal_port": webui_internal_port,
                "use_nginx": use_nginx,
                "use_ssl": False,
                "ssl_domain": None,
                "nginx_http_port": nginx_http_port if use_nginx else None,
                "nginx_https_port": None,
                "nginx_port": nginx_port if use_nginx else None,
                "litellm_external_port": litellm_external_port,
                "webui_external_port": webui_external_port,
            }
        else:
            print_error("Invalid choice. Enter 1, 2, or 3")
            continue
    
    # Manual port configuration
    # Configure all ports including nginx if selected
    print()
    print(f"{Colors.BLUE}{'═' * 59}{Colors.RESET}")
    
    if use_nginx:
        # Configure nginx port first (always random high port for rootless Docker)
        print(f"{Colors.BLUE}Nginx Port:{Colors.RESET}")
        print()
        print_info("Nginx requires random high port (rootless Docker limitation)")
        print_info("Ports < 1024 are not available without special configuration")
        print()
        nginx_port = generate_random_high_port(used_ports=host_ports_in_use)
        host_ports_in_use[nginx_port] = "Nginx HTTP"
        nginx_http_port = nginx_port
        print_success(f"Selected random high port for nginx: {nginx_port}")
        print()
        print(f"{Colors.BLUE}{'═' * 59}{Colors.RESET}")
        print(f"{Colors.BLUE}External Ports:{Colors.RESET}")
        print()
        print_info("Note: LiteLLM UI will be available directly on port (subroute not reliably supported)")
        print_info("LiteLLM API will be available through nginx at /api/litellm/")
        print()
        litellm_external_port = select_port_interactive(
            "LiteLLM UI (external)", DEFAULT_LITELLM_PORT, "Admin UI (direct access)", 
            is_internal=False,
            used_ports=host_ports_in_use,
            default_ports=default_ports
        )
        webui_external_port = None  # Open WebUI available through nginx
    elif not use_nginx:
        # Without nginx - configure external ports for each service
        print(f"{Colors.BLUE}External Ports (without nginx):{Colors.RESET}")
        print()
        litellm_external_port = select_port_interactive(
            "LiteLLM (external)", DEFAULT_LITELLM_PORT, "API and Dashboard", 
            is_internal=False,
            used_ports=host_ports_in_use,
            default_ports=default_ports
        )
        webui_external_port = select_port_interactive(
            "Open WebUI (external)", DEFAULT_WEBUI_PORT, "Web Interface", 
            is_internal=False,
            used_ports=host_ports_in_use,
            default_ports=default_ports
        )
    else:
        # With nginx: LiteLLM API available through nginx
        # LiteLLM UI needs separate external port for local network access (configuration)
        print(f"{Colors.BLUE}External Ports:{Colors.RESET}")
        print()
        print_info("With nginx:")
        print_info("  • LiteLLM API: available through nginx at /api/litellm/")
        print_info("  • Open WebUI: available through nginx at /")
        print_info("  • LiteLLM UI: needs separate port for local network access (configuration)")
        print()
        litellm_external_port = select_port_interactive(
            "LiteLLM UI (external)", DEFAULT_LITELLM_PORT, "Admin UI (local network access)", 
            is_internal=False,
            used_ports=host_ports_in_use,
            default_ports=default_ports
        )
        webui_external_port = None  # Open WebUI available through nginx
    
    # Internal ports (in order of usage frequency)
    print()
    print(f"{Colors.BLUE}{'═' * 59}{Colors.RESET}")
    
    if use_nginx:
        # With nginx - use standard internal ports (not exposed externally)
        print(f"{Colors.BLUE}Internal Ports (standard, not exposed externally):{Colors.RESET}")
        print()
        print_info("Using standard internal ports (not accessible from host):")
        print(f"  • LiteLLM (internal): {DEFAULT_LITELLM_PORT} (standard)")
        print(f"  • Open WebUI (internal): {DEFAULT_WEBUI_INTERNAL_PORT} (standard)")
        print()
        litellm_internal_port = DEFAULT_LITELLM_PORT
        webui_internal_port = DEFAULT_WEBUI_INTERNAL_PORT
    else:
        # Without nginx - internal ports can be customized
        print(f"{Colors.BLUE}Internal Ports (not accessible externally):{Colors.RESET}")
        print()
        litellm_internal_port = select_port_interactive(
            "LiteLLM (internal)", DEFAULT_LITELLM_PORT, "API proxy", 
            is_internal=True,
            used_ports=internal_ports_in_use,
            default_ports=default_ports
        )
        webui_internal_port = select_port_interactive(
            "Open WebUI (internal)", DEFAULT_WEBUI_INTERNAL_PORT, "Web Interface", 
            is_internal=True,
            used_ports=internal_ports_in_use,
            default_ports=default_ports
        )
    
    # PostgreSQL port (always internal, can be customized)
    postgres_port = select_port_interactive(
        "PostgreSQL", DEFAULT_POSTGRES_PORT, "Database", 
        is_internal=True,
        used_ports=internal_ports_in_use,
        default_ports=default_ports
    )
    
    # Ensure nginx_http_port is set if nginx is used
    if use_nginx and (nginx_http_port is None or nginx_port is None):
        raise RuntimeError("Nginx port must be set when nginx is enabled")
    
    return {
        "postgres_port": postgres_port,
        "litellm_internal_port": litellm_internal_port,
        "webui_internal_port": webui_internal_port,
        "use_nginx": use_nginx,
        "use_ssl": False,
        "ssl_domain": None,
        "nginx_http_port": nginx_http_port if use_nginx else None,
        "nginx_https_port": None,
        "nginx_port": nginx_port if use_nginx else None,
        "litellm_external_port": litellm_external_port if not use_nginx else None,
        "webui_external_port": webui_external_port if not use_nginx else None,
    }

