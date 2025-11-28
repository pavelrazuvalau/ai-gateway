"""
Start service for AI Gateway containers.

See docs/getting-started.md#step-2-start-the-system for detailed information.
"""

from pathlib import Path

from ..core.exceptions import DockerError
from ..infrastructure.docker_client import DockerClient
from ..infrastructure.file_repository import FileRepository
from ..infrastructure.logger import get_logger
from ..infrastructure.output import (
    print_access_urls,
    print_api_info,
    print_error,
    print_info,
    print_status_commands,
    print_success,
    print_warning,
)
from .services import ConfigService

logger = get_logger(__name__)


class StartService:
    """
    Service for starting Docker containers with health check waiting.

    See docs/getting-started.md#step-2-start-the-system for details.
    """

    def __init__(self, project_root: Path):
        """
        Initialize start service

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.docker_client = DockerClient()
        self.file_repo = FileRepository(self.project_root)
        self.config_service = ConfigService(self.project_root)

    def _check_virtual_key(self) -> bool:
        """
        Check if Virtual Key is present and show error if needed.

        Returns:
            True if Virtual Key is present or first run, False otherwise
        """
        virtual_key = self.config_service.get_virtual_key()
        first_run = self.config_service.is_first_run()

        if not virtual_key:
            if first_run:
                # First run - allow startup with Master Key
                # Virtual Key will be created automatically during setup
                return True
            else:
                # Not first run - Virtual Key is required
                print_error("❌ Virtual Key not found in .env")
                print()
                print_error(
                    "Virtual Key is required for Open WebUI to work properly"
                )
                print_error(
                    "Master Key should not be used directly for security reasons"
                )
                print()
                print_info("To create Virtual Key:")
                import sys

                if sys.platform == "win32":
                    print_info("   virtual-key.bat")
                    print_info("   # Or: python -m src.virtual_key")
                else:
                    print_info("   ./virtual-key.sh")
                    print_info("   # Or: python3 -m src.virtual_key")
                print()
                print_info(
                    "After creating Virtual Key, it will be saved to .env automatically"
                )
                print()
                return False

        return True

    def _update_web_search_settings(self) -> None:
        """Update OpenWebUI web search settings from environment variables if flag is set"""
        if not self.config_service.should_update_web_search_settings():
            return

        try:
            from ..infrastructure.openwebui_db import (
                update_web_search_settings_on_start,
            )

            print_info(
                "Updating OpenWebUI web search settings from environment variables..."
            )
            if update_web_search_settings_on_start("open-webui"):
                print_success(
                    "✅ OpenWebUI web search settings updated"
                )
                # Clear flag after successful update
                self._clear_update_web_search_flag()
            else:
                print_warning(
                    "⚠️  Could not update OpenWebUI settings (will retry on next start)"
                )
        except Exception as e:
            logger.warning(f"Error updating web search settings: {e}")
            # Don't fail startup if we can't update settings

    def _create_virtual_key_on_first_run(self) -> None:
        """Auto-create Virtual Key on first run if not exists"""
        virtual_key = self.config_service.get_virtual_key()
        first_run = self.config_service.is_first_run()

        if virtual_key or not first_run:
            return

        # Wait for LiteLLM to be ready, then create Virtual Key automatically
        print_info(
            "🔑 Creating Virtual Key automatically on first run..."
        )
        print_info("Waiting for LiteLLM to be ready...")

        import time

        # Wait for LiteLLM to be ready (max 60 seconds)
        for _i in range(30):
            try:
                import requests

                response = requests.get(
                    "http://localhost:4000/health/liveliness", timeout=2
                )
                if response.status_code == 200:
                    break
            except Exception:
                pass
            time.sleep(2)

        # Try to create Virtual Key
        from ..virtual_key import run_inside_docker_container

        master_key = self.config_service.get_master_key()

        if master_key:
            virtual_key = run_inside_docker_container(
                self.project_root, master_key
            )

            if virtual_key:
                # Save Virtual Key to .env
                self._save_virtual_key_to_env(virtual_key)
                print_success(
                    "✅ Virtual Key created and saved to .env"
                )
                print_info(f"   Key: {virtual_key[:30]}...")
                print()
            else:
                print_warning(
                    "⚠️  Could not create Virtual Key automatically"
                )
                print_info(
                    "   You can create it manually: ./virtual-key.sh"
                )
                print()

    def _save_virtual_key_to_env(self, virtual_key: str) -> None:
        """Save Virtual Key to .env file"""
        env_file = self.project_root / ".env"
        content = env_file.read_text(encoding="utf-8")

        # Update or add VIRTUAL_KEY
        lines = content.split("\n")
        new_lines = []
        virtual_key_added = False

        for line in lines:
            if line.startswith("VIRTUAL_KEY="):
                new_lines.append(f"VIRTUAL_KEY={virtual_key}")
                virtual_key_added = True
            elif (
                line.strip().startswith("# Virtual Key")
                and not virtual_key_added
            ):
                # Add Virtual Key after comment
                new_lines.append(line)
                new_lines.append(f"VIRTUAL_KEY={virtual_key}")
                virtual_key_added = True
            else:
                new_lines.append(line)

        if not virtual_key_added:
            # Add at the end
            new_lines.append("")
            new_lines.append(
                "# Virtual Key for Open WebUI (auto-created on first run)"
            )
            new_lines.append(f"VIRTUAL_KEY={virtual_key}")

        env_file.write_text(
            "\n".join(new_lines), encoding="utf-8"
        )

        # Update FIRST_RUN flag
        content = env_file.read_text(encoding="utf-8")
        content = content.replace(
            "FIRST_RUN=yes", "FIRST_RUN=no"
        )
        env_file.write_text(content, encoding="utf-8")

    def _handle_failed_containers(self) -> None:
        """Show information about failed containers"""
        failed_containers = self.docker_client.get_failed_containers(
            str(self.project_root)
        )

        if failed_containers:
            print()
            print_error("❌ Some containers failed to start:")
            print()
            for container in failed_containers:
                print_error(
                    f"  • {container['name']}: {container['state']} (exit code: {container['exit_code']})"
                )
                # Get and show logs for failed container
                logs = self.docker_client.get_container_logs(
                    str(self.project_root), container["name"], tail=30
                )
                if logs.strip():
                    print()
                    print_info(f"  Logs from {container['name']}:")
                    # Show last few lines of logs
                    log_lines = logs.strip().split("\n")
                    for line in log_lines[-10:]:  # Last 10 lines
                        print(f"    {line}")
                    print()

    def _print_stop_instructions(self) -> None:
        """Print instructions for stopping containers"""
        print()
        print_info("To stop all containers:")
        import sys

        if sys.platform == "win32":
            print_info("   stop.bat  # Windows")
        else:
            print_info("   ./stop.sh  # Linux/macOS")
        print()

    def start_containers(self, wait_for_healthy: bool = True) -> bool:
        """
        Start Docker containers and wait for them to become healthy.

        See docs/troubleshooting.md#containers-wont-start for troubleshooting.

        Args:
            wait_for_healthy: Whether to wait for containers to become healthy

        Returns:
            True if containers started successfully, False otherwise
        """
        try:
            # Check for Virtual Key (required for Open WebUI)
            if not self._check_virtual_key():
                return False

            # Clean up any existing containers with conflicting names before starting
            # This is important for E2E tests where containers might not have been cleaned up
            # Note: container_name in docker-compose.yml ignores COMPOSE_PROJECT_NAME,
            # so we need to clean up manually
            try:
                self.docker_client.compose_down(str(self.project_root), timeout=30)
            except Exception:
                # Ignore errors - containers might not exist
                pass
            
            # Also remove containers with fixed names that might conflict
            # (container_name in docker-compose.yml ignores COMPOSE_PROJECT_NAME)
            import subprocess
            fixed_container_names = ["litellm-postgres", "litellm-proxy", "open-webui", "litellm-nginx"]
            for container_name in fixed_container_names:
                try:
                    subprocess.run(
                        ["docker", "rm", "-f", container_name],
                        capture_output=True,
                        timeout=10,
                        check=False,  # Don't fail if container doesn't exist
                    )
                except Exception:
                    pass  # Ignore errors

            print_info("Starting containers...")

            # Try to use --wait flag (Docker Compose v2.3+)
            try:
                self.docker_client.compose_up(
                    str(self.project_root), detach=True, wait=wait_for_healthy
                )

                # Update web search settings from environment variables if flag is set
                # This happens when profile was changed during setup
                self._update_web_search_settings()

                if wait_for_healthy:
                    print_success("Containers started and healthy!")
                else:
                    print_success("Containers started successfully!")

                # Auto-create Virtual Key on first run if not exists
                if wait_for_healthy:
                    self._create_virtual_key_on_first_run()

                return True
            except DockerError:
                # If --wait failed, check for failed containers and show their logs
                self._handle_failed_containers()

                # Show error and instructions
                print()
                print_error("Failed to start containers")
                self._print_stop_instructions()
                print_info("To view all logs:")
                print_info("   docker compose logs")
                print()
                return False

        except DockerError as e:
            print_error(f"Failed to start containers: {e}")
            self._print_stop_instructions()
            return False
        except Exception as e:
            logger.exception("Unexpected error starting containers")
            print_error(f"Unexpected error: {e}")
            self._print_stop_instructions()
            return False

    def check_container_status(self) -> tuple[bool, list[str]]:
        """
        Check container status for errors

        Returns:
            Tuple of (has_errors, list of error messages)
        """
        import json
        import subprocess

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
                timeout=10,
            )

            if not result.stdout.strip():
                return False, []

            containers = []
            for line in result.stdout.strip().split("\n"):
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

        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ) as e:
            logger.warning(f"Error checking container status: {e}")
            return False, []

    def _get_local_ip(self) -> str:
        """Get local network IP address from primary interface (ethernet/wifi, not VPN)"""
        try:
            import re
            import subprocess

            # VPN interface patterns to exclude
            vpn_patterns = [
                r"^tun\d+",  # OpenVPN, WireGuard
                r"^tap\d+",  # TAP interfaces
                r"^wg\d+",  # WireGuard
                r"^vpn\d+",  # VPN interfaces
                r"^ppp\d+",  # PPP (may be VPN)
                r"^veth",  # Virtual ethernet (Docker)
                r"^docker",  # Docker interfaces
                r"^br-",  # Docker bridges
                r"^virbr",  # Virtual bridges
            ]

            # Primary interface patterns (priority order)
            primary_patterns = [
                r"^eth\d+",  # Ethernet (old naming)
                r"^enp\d+",  # Ethernet (predictable naming)
                r"^ens\d+",  # Ethernet (predictable naming)
                r"^enx",  # Ethernet (MAC-based)
                r"^wlan\d+",  # WiFi (old naming)
                r"^wlp\d+",  # WiFi (predictable naming)
                r"^wlx",  # WiFi (MAC-based)
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
                ["ip", "addr", "show"], capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                current_interface = None
                primary_ips = []  # IPs from primary interfaces
                other_ips = []  # IPs from other non-VPN interfaces

                for line in result.stdout.split("\n"):
                    # Check for interface name (e.g., "2: enp6s18: ...")
                    interface_match = re.match(r"^\d+:\s+([^:]+):", line)
                    if interface_match:
                        current_interface = interface_match.group(1)
                        continue

                    # Check for IP address
                    if current_interface and "inet " in line:
                        # Extract IP from line like "inet 192.168.1.100/24"
                        ip_match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)/", line)
                        if ip_match:
                            ip = ip_match.group(1)

                            # Skip loopback and link-local
                            if ip.startswith("127.") or ip.startswith("169.254."):
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
                    timeout=2,
                )
                if result.returncode == 0:
                    # Extract interface from output like "8.8.8.8 via 192.168.1.1 dev eth0 src 192.168.1.100"
                    match = re.search(
                        r"dev\s+(\S+)\s+src\s+(\d+\.\d+\.\d+\.\d+)", result.stdout
                    )
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
                s.connect(("8.8.8.8", 80))
                socket_ip: str = s.getsockname()[0]
                # Skip loopback
                if not socket_ip.startswith("127."):
                    return socket_ip
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
            # Load configuration
            self.config_service.load_from_env()
            config = self.config_service.get_config()
            port_config = config.port_config

            use_nginx = port_config.use_nginx
            litellm_external_port = (
                str(port_config.litellm_external_port)
                if port_config.litellm_external_port
                else None
            )
            webui_port = (
                str(port_config.webui_external_port)
                if port_config.webui_external_port
                else "3000"
            )
            nginx_http_port = (
                port_config.nginx_http_port or port_config.nginx_port
            )

            # Get local network IP
            local_ip = self._get_local_ip()

            # Print access URLs
            print_access_urls(
                local_ip=local_ip,
                use_nginx=use_nginx,
                nginx_http_port=nginx_http_port,
                webui_port=webui_port,
                litellm_external_port=litellm_external_port,
            )

            # Print API info (only if using nginx)
            if use_nginx and nginx_http_port:
                virtual_key = self.config_service.get_virtual_key()
                print_api_info(
                    local_ip=local_ip,
                    nginx_http_port=nginx_http_port,
                    virtual_key=virtual_key if virtual_key else None,
                    use_nginx=use_nginx,
                )

            # Print status commands
            print_status_commands()

        except Exception as e:
            logger.warning(f"Error reading access info: {e}")

    def show_first_run_instructions(self) -> None:
        """
        Show Virtual Key setup instructions on first run and optionally run setup script.

        See docs/getting-started.md#step-31-create-virtual-key-required for details.
        """
        try:
            if not self.config_service.is_first_run():
                return

            print()
            print_info("💡 First Run Detected!")
            print()
            print_info(
                "To complete setup, configure Virtual Key for Open WebUI:"
            )
            print()
            print_info("The setup script will:")
            print_info(
                "   • Create Virtual Key in LiteLLM (via API or manual)"
            )
            print_info(
                "   • Provide instructions for Open WebUI configuration"
            )
            print()
            print_info("After setup, configure Open WebUI:")
            print_info("   • Open Open WebUI in browser")
            print_info("   • Go to Settings -> Connections")
            print_info("   • Add connection with Virtual Key")
            print()
            print_warning("⚠️  Using Master Key directly is less secure")
            print_info(
                "   Virtual Key allows better access control and monitoring"
            )
            print()

            # Ask user if they want to run setup script now
            try:
                response = (
                    input("Would you like to run Virtual Key setup script now? [Y/n]: ")
                    .strip()
                    .lower()
                )
                if response and response not in ("y", "yes", ""):
                    print()
                    print_info("You can run the setup script later:")
                    import sys

                    if sys.platform == "win32":
                        print_info("   virtual-key.bat")
                        print_info("   # Or: python -m src.virtual_key")
                    else:
                        print_info("   ./virtual-key.sh")
                        print_info("   # Or: python3 -m src.virtual_key")
                    print()
                    return

                # Run setup script
                print()
                print_info("🚀 Running Virtual Key setup script...")
                print()

                import subprocess
                import sys

                # Run the Python module
                result = subprocess.run(
                    [sys.executable, "-m", "src.virtual_key"],
                    cwd=str(self.project_root),
                    check=False,
                )

                if result.returncode == 0:
                    print()
                    print_success("✅ Virtual Key setup completed!")
                    print()
                    print_info("Next steps:")
                    print_info("   1. Open Open WebUI in browser")
                    print_info("   2. Go to Settings -> Connections")
                    print_info(
                        "   3. Add connection with the Virtual Key you just created"
                    )
                    print()
                else:
                    print()
                    print_warning("⚠️  Setup script exited with errors")
                    print_info("You can run it manually later:")
                    if sys.platform == "win32":
                        print_info("   virtual-key.bat")
                        print_info("   # Or: python -m src.virtual_key")
                    else:
                        print_info("   ./virtual-key.sh")
                        print_info("   # Or: python3 -m src.virtual_key")
                    print()

            except KeyboardInterrupt:
                print()
                print_warning("Setup cancelled by user")
                print()
            except Exception as e:
                logger.warning(f"Error running setup script: {e}")
                print_warning(
                    f"Could not run setup script automatically: {e}"
                )
                print_info("You can run it manually:")
                import sys

                if sys.platform == "win32":
                    print_info("   virtual-key.bat")
                    print_info("   # Or: python -m src.virtual_key")
                else:
                    print_info("   ./virtual-key.sh")
                    print_info("   # Or: python3 -m src.virtual_key")
                print()

        except Exception as e:
            logger.warning(f"Error showing first run instructions: {e}")

    def check_models_and_suggest_continue_dev(self) -> None:
        """
        Check if models are available via Virtual Key and suggest Continue.dev setup.

        See docs/integrations/continue-dev.md for Continue.dev integration details.
        """
        try:
            from .continue_dev_service import ContinueDevService

            virtual_key = self.config_service.get_virtual_key()

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
            print_info("🔍 Checking if models are configured...")
            has_models, model_count = continue_service.check_models_available(
                api_base, virtual_key
            )

            if has_models:
                print()
                print_success(
                    f"✅ Found {model_count} model(s) configured in LiteLLM"
                )
                print()
                print_info("💡 Continue.dev Integration Available")
                print_info(
                    "   You can generate Continue.dev configuration for VS Code extension"
                )
                print()

                try:
                    response = (
                        input("Would you like to configure Continue.dev now? [y/N]: ")
                        .strip()
                        .lower()
                    )
                    if response in ("y", "yes"):
                        print()
                        print_info(
                            "🚀 Starting Continue.dev configuration..."
                        )
                        print()

                        # Run Continue.dev setup
                        result = continue_service.run_setup_interactive()
                        if result == 0:
                            print()
                            print_success(
                                "✅ Continue.dev configuration completed!"
                            )
                            print()
                        else:
                            print()
                            print_warning(
                                "⚠️  Continue.dev setup had some issues"
                            )
                            print_info("You can run it manually later:")
                            print_info("   ./ai-gateway continue-dev")
                            print()
                    else:
                        print()
                        print_info("You can configure Continue.dev later:")
                        print_info("   ./ai-gateway continue-dev")
                        print()
                except KeyboardInterrupt:
                    print()
                    print_warning("Continue.dev setup cancelled")
                    print()
            else:
                # Models not configured yet
                print()
                print_info("ℹ️  No models found yet")
                print_info("   Configure models in LiteLLM Admin UI first")
                print_info("   Then run: ./ai-gateway continue-dev")
                print()

        except Exception as e:
            logger.warning(f"Error checking models for Continue.dev: {e}")

    def _clear_update_web_search_flag(self) -> None:
        """Clear UPDATE_WEB_SEARCH_SETTINGS flag from .env after successful update"""
        try:
            env_file = self.project_root / ".env"
            if not env_file.exists():
                return

            # Read current .env
            env_vars = self.file_repo.read_env_file(env_file)

            # Remove flag
            if "UPDATE_WEB_SEARCH_SETTINGS" in env_vars:
                del env_vars["UPDATE_WEB_SEARCH_SETTINGS"]

                # Write back to .env
                with open(env_file, "w") as f:
                    for key, value in env_vars.items():
                        # Escape special characters in value
                        if " " in value or "#" in value or "$" in value:
                            f.write(f'{key}="{value}"\n')
                        else:
                            f.write(f"{key}={value}\n")

                logger.debug("Cleared UPDATE_WEB_SEARCH_SETTINGS flag from .env")
        except Exception as e:
            logger.warning(f"Could not clear UPDATE_WEB_SEARCH_SETTINGS flag: {e}")
