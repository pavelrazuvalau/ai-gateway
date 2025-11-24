"""
Start service for AI Gateway containers
"""

from pathlib import Path
from typing import Optional
from ..core.exceptions import DockerError
from ..infrastructure.docker_client import DockerClient
from ..infrastructure.logger import get_logger

logger = get_logger(__name__)


class StartService:
    """Service for starting Docker containers with health check waiting"""
    
    def __init__(self, project_root: Path):
        """
        Initialize start service
        
        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.docker_client = DockerClient()
        self.utils = self._import_utils()
    
    def _import_utils(self):
        """Import utility functions"""
        from types import SimpleNamespace
        from ..utils import (
            print_info, print_success, print_warning,
            print_error, Colors, read_env_file
        )
        return SimpleNamespace(
            print_info=print_info,
            print_success=print_success,
            print_warning=print_warning,
            print_error=print_error,
            Colors=Colors,
            read_env_file=read_env_file,
        )
    
    def start_containers(self, wait_for_healthy: bool = True) -> bool:
        """
        Start Docker containers and wait for them to become healthy
        
        Args:
            wait_for_healthy: Whether to wait for containers to become healthy
        
        Returns:
            True if containers started successfully, False otherwise
        """
        try:
            # Check for Virtual Key (required for Open WebUI)
            env_vars = self.utils.read_env_file(self.project_root / ".env")
            virtual_key = env_vars.get("VIRTUAL_KEY", "").strip()
            first_run = env_vars.get("FIRST_RUN", "no").lower() in ("yes", "true", "1")
            
            if not virtual_key:
                if first_run:
                    # First run - allow startup with Master Key
                    # Virtual Key will be created automatically during setup
                    # No need to show warning here - setup will handle it
                    # Continue with startup
                    pass
                else:
                    # Not first run - Virtual Key is required
                    self.utils.print_error("❌ Virtual Key not found in .env")
                    print()
                    self.utils.print_error("Virtual Key is required for Open WebUI to work properly")
                    self.utils.print_error("Master Key should not be used directly for security reasons")
                    print()
                    self.utils.print_info("To create Virtual Key:")
                    import sys
                    if sys.platform == "win32":
                        self.utils.print_info("   python virtual-key.py")
                    else:
                        self.utils.print_info("   python3 virtual-key.py")
                        self.utils.print_info("   # Or: ./virtual-key.sh")
                    print()
                    self.utils.print_info("After creating Virtual Key, it will be saved to .env automatically")
                    print()
                    return False
            
            self.utils.print_info("Starting containers...")
            
            # Try to use --wait flag (Docker Compose v2.3+)
            try:
                self.docker_client.compose_up(str(self.project_root), detach=True, wait=wait_for_healthy)
                if wait_for_healthy:
                    self.utils.print_success("Containers started and healthy!")
                else:
                    self.utils.print_success("Containers started successfully!")
                return True
            except DockerError as e:
                # If --wait failed, check for failed containers and show their logs
                failed_containers = self.docker_client.get_failed_containers(str(self.project_root))
                
                if failed_containers:
                    print()
                    self.utils.print_error("❌ Some containers failed to start:")
                    print()
                    for container in failed_containers:
                        self.utils.print_error(f"  • {container['name']}: {container['state']} (exit code: {container['exit_code']})")
                        # Get and show logs for failed container
                        logs = self.docker_client.get_container_logs(
                            str(self.project_root),
                            container['name'],
                            tail=30
                        )
                        if logs.strip():
                            print()
                            self.utils.print_info(f"  Logs from {container['name']}:")
                            # Show last few lines of logs
                            log_lines = logs.strip().split('\n')
                            for line in log_lines[-10:]:  # Last 10 lines
                                print(f"    {line}")
                            print()
                
                # Show error and instructions
                print()
                self.utils.print_error("Failed to start containers")
                print()
                self.utils.print_info("To stop all containers:")
                self.utils.print_info("   ./stop.sh  # Linux/macOS")
                self.utils.print_info("   stop.bat  # Windows")
                print()
                self.utils.print_info("To view all logs:")
                self.utils.print_info("   docker compose logs")
                print()
                return False
                    
        except DockerError as e:
            self.utils.print_error(f"Failed to start containers: {e}")
            print()
            self.utils.print_info("To stop all containers:")
            self.utils.print_info("   ./stop.sh  # Linux/macOS")
            self.utils.print_info("   stop.bat  # Windows")
            print()
            return False
        except Exception as e:
            logger.exception("Unexpected error starting containers")
            self.utils.print_error(f"Unexpected error: {e}")
            print()
            self.utils.print_info("To stop all containers:")
            self.utils.print_info("   ./stop.sh  # Linux/macOS")
            self.utils.print_info("   stop.bat  # Windows")
            print()
            return False
    
    def check_container_status(self) -> tuple[bool, list[str]]:
        """
        Check container status for errors
        
        Returns:
            Tuple of (has_errors, list of error messages)
        """
        import subprocess
        import json
        
        errors = []
        has_errors = False
        
        try:
            # Get container status
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                return False, []
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            # Check for exited/error containers
            for container in containers:
                state = container.get("State", "")
                service = container.get("Service", "")
                health = container.get("Health", "")
                
                if not service:
                    continue
                
                # Check for exited containers
                if "exited" in state.lower() or "dead" in state.lower():
                    has_errors = True
                    exit_code = container.get("ExitCode", "?")
                    errors.append(f"Container {service} exited with code {exit_code}")
                
                # Check for unhealthy containers
                if health and health.lower() not in ("healthy", ""):
                    has_errors = True
                    errors.append(f"Container {service} is unhealthy: {health}")
            
            return has_errors, errors
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Error checking container status: {e}")
            return False, []
    
    def _get_local_ip(self) -> str:
        """Get local network IP address from primary interface (ethernet/wifi, not VPN)"""
        try:
            import subprocess
            import re
            
            # VPN interface patterns to exclude
            vpn_patterns = [
                r'^tun\d+',      # OpenVPN, WireGuard
                r'^tap\d+',      # TAP interfaces
                r'^wg\d+',       # WireGuard
                r'^vpn\d+',      # VPN interfaces
                r'^ppp\d+',      # PPP (may be VPN)
                r'^veth',        # Virtual ethernet (Docker)
                r'^docker',      # Docker interfaces
                r'^br-',         # Docker bridges
                r'^virbr',       # Virtual bridges
            ]
            
            # Primary interface patterns (priority order)
            primary_patterns = [
                r'^eth\d+',      # Ethernet (old naming)
                r'^enp\d+',      # Ethernet (predictable naming)
                r'^ens\d+',      # Ethernet (predictable naming)
                r'^enx',         # Ethernet (MAC-based)
                r'^wlan\d+',     # WiFi (old naming)
                r'^wlp\d+',      # WiFi (predictable naming)
                r'^wlx',         # WiFi (MAC-based)
            ]
            
            def is_vpn_interface(name: str) -> bool:
                """Check if interface is a VPN interface"""
                for pattern in vpn_patterns:
                    if re.match(pattern, name):
                        return True
                return False
            
            def is_primary_interface(name: str) -> bool:
                """Check if interface is a primary interface (ethernet/wifi)"""
                for pattern in primary_patterns:
                    if re.match(pattern, name):
                        return True
                return False
            
            # Get all network interfaces
            result = subprocess.run(
                ["ip", "addr", "show"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                current_interface = None
                primary_ips = []  # IPs from primary interfaces
                other_ips = []    # IPs from other non-VPN interfaces
                
                for line in result.stdout.split('\n'):
                    # Check for interface name (e.g., "2: enp6s18: ...")
                    interface_match = re.match(r'^\d+:\s+([^:]+):', line)
                    if interface_match:
                        current_interface = interface_match.group(1)
                        continue
                    
                    # Check for IP address
                    if current_interface and 'inet ' in line:
                        # Extract IP from line like "inet 192.168.1.100/24"
                        ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)/', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            
                            # Skip loopback and link-local
                            if ip.startswith('127.') or ip.startswith('169.254.'):
                                continue
                            
                            # Skip VPN interfaces
                            if is_vpn_interface(current_interface):
                                continue
                            
                            # Prioritize primary interfaces (ethernet/wifi)
                            if is_primary_interface(current_interface):
                                primary_ips.append((current_interface, ip))
                            else:
                                # Other non-VPN interfaces (fallback)
                                other_ips.append((current_interface, ip))
                
                # Return first IP from primary interface, or first from other interfaces
                if primary_ips:
                    return primary_ips[0][1]
                elif other_ips:
                    return other_ips[0][1]
            
            # Fallback: try to get default route interface
            try:
                result = subprocess.run(
                    ["ip", "route", "get", "8.8.8.8"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    # Extract interface from output like "8.8.8.8 via 192.168.1.1 dev eth0 src 192.168.1.100"
                    match = re.search(r'dev\s+(\S+)\s+src\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if match:
                        interface = match.group(1)
                        ip = match.group(2)
                        # Only return if not VPN interface
                        if not is_vpn_interface(interface):
                            return ip
            except Exception:
                pass
            
        except Exception:
            pass
        
        # Final fallback: try socket method (may not work if no default route)
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Connect to a public DNS (doesn't actually connect)
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
                # Skip loopback
                if not ip.startswith('127.'):
                    return ip
            except Exception:
                pass
            finally:
                s.close()
        except Exception:
            pass
        
        # Last resort fallback
        return "localhost"
    
    def print_access_info(self) -> None:
        """Print access information based on configuration"""
        try:
            env_vars = self.utils.read_env_file(self.project_root / ".env")
            
            use_nginx = env_vars.get("USE_NGINX", "no").lower() in ("yes", "true", "1")
            litellm_external_port = env_vars.get("LITELLM_EXTERNAL_PORT", "").strip()
            if not litellm_external_port:
                litellm_external_port = None
            webui_port = env_vars.get("WEBUI_EXTERNAL_PORT", "3000")
            nginx_http_port = env_vars.get("NGINX_HTTP_PORT", "").strip()
            if not nginx_http_port:
                # Fallback to NGINX_PORT if NGINX_HTTP_PORT is not set
                nginx_http_port = env_vars.get("NGINX_PORT", "").strip()
            if not nginx_http_port:
                nginx_http_port = None
            
            # Get local network IP
            local_ip = self._get_local_ip()
            
            print()
            self.utils.print_info("🌐 Access URLs (local network):")
            print()
            
            if use_nginx:
                print(f"  • Open WebUI: http://{local_ip}:{nginx_http_port}")
                
                # Check for Virtual Key
                virtual_key = env_vars.get("VIRTUAL_KEY", "").strip()
                api_url = f"http://{local_ip}:{nginx_http_port}/api/litellm/v1"
                
                if virtual_key:
                    print(f"  • LiteLLM API: {api_url}")
                    print(f"    API Key: {virtual_key}")
                    print()
                    self.utils.print_info("💡 Use this API Key for external clients (agents, scripts, etc.)")
                    self.utils.print_info("   ✅ Open WebUI is configured to use Virtual Key automatically")
                    print()
                else:
                    print(f"  • LiteLLM API: {api_url}")
                    print(f"    API Key: Use Master Key or run ./virtual-key.py to create Virtual Key")
                    print()
                    self.utils.print_warning("⚠️  Virtual Key not configured - Open WebUI uses Master Key")
                    self.utils.print_info("   Run ./virtual-key.py to create Virtual Key for better security")
                    print()
                
                if litellm_external_port:
                    print(f"  • LiteLLM UI: http://{local_ip}:{litellm_external_port}/ui")
                else:
                    # Try to get port from docker-compose if not in .env
                    self.utils.print_warning("  • LiteLLM UI: port not configured, check docker-compose.override.yml")
                print()
                self.utils.print_info("ℹ️  Note: LiteLLM UI accessible only from local/VPN network (security)")
                print()
                self.utils.print_info("💡 Note: Configure SSL/HTTPS via your own nginx container")
            else:
                print(f"  • Open WebUI: http://{local_ip}:{webui_port}")
                print(f"  • LiteLLM API: http://{local_ip}:{litellm_external_port}")
                print(f"  • LiteLLM Admin UI: http://{local_ip}:{litellm_external_port}/ui")
            
            print()
            self.utils.print_info("📊 Check status:")
            print("  docker compose ps")
            print()
            self.utils.print_info("📝 View logs:")
            print("  docker compose logs -f")
            print()
            
        except Exception as e:
            logger.warning(f"Error reading access info: {e}")
    
    def show_first_run_instructions(self) -> None:
        """Show Virtual Key setup instructions on first run and optionally run setup script"""
        try:
            env_vars = self.utils.read_env_file(self.project_root / ".env")
            first_run = env_vars.get("FIRST_RUN", "no").lower() in ("yes", "true", "1")
            
            if not first_run:
                return
            
            print()
            self.utils.print_info("💡 First Run Detected!")
            print()
            self.utils.print_info("To complete setup, configure Virtual Key for Open WebUI:")
            print()
            self.utils.print_info("The setup script will:")
            self.utils.print_info("   • Create Virtual Key in LiteLLM (via API or manual)")
            self.utils.print_info("   • Provide instructions for Open WebUI configuration")
            print()
            self.utils.print_info("After setup, configure Open WebUI:")
            self.utils.print_info("   • Open Open WebUI in browser")
            self.utils.print_info("   • Go to Settings -> Connections")
            self.utils.print_info("   • Add connection with Virtual Key")
            print()
            self.utils.print_warning("⚠️  Using Master Key directly is less secure")
            self.utils.print_info("   Virtual Key allows better access control and monitoring")
            print()
            
            # Ask user if they want to run setup script now
            try:
                response = input("Would you like to run Virtual Key setup script now? [Y/n]: ").strip().lower()
                if response and response not in ('y', 'yes', ''):
                    print()
                    self.utils.print_info("You can run the setup script later:")
                    import sys
                    if sys.platform == "win32":
                        self.utils.print_info("   python virtual-key.py")
                        self.utils.print_info("   # Or: virtual-key.bat")
                    else:
                        self.utils.print_info("   python3 virtual-key.py")
                        self.utils.print_info("   # Or: ./virtual-key.sh")
                    print()
                    return
                
                # Run setup script
                print()
                self.utils.print_info("🚀 Running Virtual Key setup script...")
                print()
                
                import subprocess
                import sys
                
                # Try to run the universal Python script
                setup_script = self.project_root / "virtual-key.py"
                if setup_script.exists():
                    # Run as script
                    if sys.platform == "win32":
                        result = subprocess.run(
                            [sys.executable, str(setup_script)],
                            cwd=str(self.project_root),
                            check=False
                        )
                    else:
                        result = subprocess.run(
                            [sys.executable, str(setup_script)],
                            cwd=str(self.project_root),
                            check=False
                        )
                else:
                    # Fallback to module import
                    result = subprocess.run(
                        [sys.executable, "-m", "src.virtual_key"],
                        cwd=str(self.project_root),
                        check=False
                    )
                
                if result.returncode == 0:
                    print()
                    self.utils.print_success("✅ Virtual Key setup completed!")
                    print()
                    self.utils.print_info("Next steps:")
                    self.utils.print_info("   1. Open Open WebUI in browser")
                    self.utils.print_info("   2. Go to Settings -> Connections")
                    self.utils.print_info("   3. Add connection with the Virtual Key you just created")
                    print()
                else:
                    print()
                    self.utils.print_warning("⚠️  Setup script exited with errors")
                    self.utils.print_info("You can run it manually later:")
                    if sys.platform == "win32":
                        self.utils.print_info("   python virtual-key.py")
                    else:
                        self.utils.print_info("   python3 virtual-key.py")
                    print()
                    
            except KeyboardInterrupt:
                print()
                self.utils.print_warning("Setup cancelled by user")
                print()
            except Exception as e:
                logger.warning(f"Error running setup script: {e}")
                self.utils.print_warning(f"Could not run setup script automatically: {e}")
                self.utils.print_info("You can run it manually:")
                import sys
                if sys.platform == "win32":
                    self.utils.print_info("   python virtual-key.py")
                else:
                    self.utils.print_info("   python3 virtual-key.py")
                print()
            
        except Exception as e:
            logger.warning(f"Error showing first run instructions: {e}")
    
    def check_models_and_suggest_continue_dev(self) -> None:
        """
        Check if models are available via Virtual Key and suggest Continue.dev setup
        """
        try:
            from .continue_dev_service import ContinueDevService
            
            env_vars = self.utils.read_env_file(self.project_root / ".env")
            virtual_key = env_vars.get("VIRTUAL_KEY", "").strip()
            
            if not virtual_key:
                # No Virtual Key - can't check models
                return
            
            # Get API configuration
            continue_service = ContinueDevService(self.project_root)
            api_base, _, _ = continue_service.get_api_config_from_env()
            
            if not api_base:
                # Can't determine API base URL
                return
            
            # Check if models are available
            print()
            self.utils.print_info("🔍 Checking if models are configured...")
            has_models, model_count = continue_service.check_models_available(api_base, virtual_key)
            
            if has_models:
                print()
                self.utils.print_success(f"✅ Found {model_count} model(s) configured in LiteLLM")
                print()
                self.utils.print_info("💡 Continue.dev Integration Available")
                self.utils.print_info("   You can generate Continue.dev configuration for VS Code extension")
                print()
                
                try:
                    response = input("Would you like to configure Continue.dev now? [y/N]: ").strip().lower()
                    if response in ('y', 'yes'):
                        print()
                        self.utils.print_info("🚀 Starting Continue.dev configuration...")
                        print()
                        
                        # Run Continue.dev setup
                        result = continue_service.run_setup_interactive()
                        if result == 0:
                            print()
                            self.utils.print_success("✅ Continue.dev configuration completed!")
                            print()
                        else:
                            print()
                            self.utils.print_warning("⚠️  Continue.dev setup had some issues")
                            self.utils.print_info("You can run it manually later:")
                            self.utils.print_info("   ./ai-gateway continue-dev")
                            print()
                    else:
                        print()
                        self.utils.print_info("You can configure Continue.dev later:")
                        self.utils.print_info("   ./ai-gateway continue-dev")
                        print()
                except KeyboardInterrupt:
                    print()
                    self.utils.print_warning("Continue.dev setup cancelled")
                    print()
            else:
                # Models not configured yet
                print()
                self.utils.print_info("ℹ️  No models found yet")
                self.utils.print_info("   Configure models in LiteLLM Admin UI first")
                self.utils.print_info("   Then run: ./ai-gateway continue-dev")
                print()
                
        except Exception as e:
            logger.warning(f"Error checking models for Continue.dev: {e}")

