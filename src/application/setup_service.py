"""
Setup service for AI Gateway configuration.

See docs/getting-started.md#step-1-run-setup-script for detailed information.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
from ..core.config import ResourceProfile, BudgetProfile, PortConfig, AppConfig
from ..core.constants import (
    DEFAULT_UI_USERNAME, DEFAULT_POSTGRES_USER, DEFAULT_POSTGRES_DB,
    BUDGET_PROFILE_TEST, YES_VALUES, NO_VALUES
)
from ..core.exceptions import ConfigurationError, FileOperationError, DockerError
from ..infrastructure.file_repository import FileRepository
from ..infrastructure.security import SecurityService
from ..infrastructure.docker_client import DockerClient
from ..infrastructure.logger import get_logger
from ..application.services import ConfigService

logger = get_logger(__name__)


class InteractiveSetup:
    """
    Interactive setup flow.
    
    See docs/getting-started.md#step-1-run-setup-script for details.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.utils = self._import_utils()
    
    def _import_utils(self):
        """Import utility functions"""
        from types import SimpleNamespace
        from ..utils import (
            print_header, print_info, print_warning, print_error,
            print_success, Colors, read_env_file
        )
        return SimpleNamespace(
            print_header=print_header,
            print_info=print_info,
            print_warning=print_warning,
            print_error=print_error,
            print_success=print_success,
            Colors=Colors,
            read_env_file=read_env_file,
        )
    
    def ask_env_mode(self) -> Tuple[bool, bool, Dict[str, str]]:
        """
        Ask user about .env file mode
        
        Returns:
            Tuple of (reuse_env, force_recreate, existing_env)
        """
        import os
        
        if not os.path.exists(".env"):
            self.utils.print_info(".env file not found — will create new one")
            self.utils.print_info("After startup, all settings can be configured through LiteLLM Admin UI")
            # When creating new .env, we need to recreate containers to apply new passwords
            return False, True, {}
        
        self.utils.print_info(".env file already exists")
        self.utils.print_info("All settings are configured through LiteLLM Admin UI")
        print()  # Empty line for readability
        self.utils.print_info("Select operation mode:")
        self.utils.print_info("  [1] Use existing .env (preserve all settings, passwords and keys)")
        self.utils.print_info("  [2] Create new .env (recreate system from scratch)")
        print()  # Empty line before input
        
        choice = input("Select option [1-2]: ").strip()
        
        if choice == "2":
            return self._handle_new_env()
        else:
            existing_env = self.utils.read_env_file(".env")
            if existing_env:
                self.utils.print_success("Existing .env will be used")
                self.utils.print_info("Settings will be updated, but passwords and keys will remain unchanged")
            return True, False, existing_env
    
    def _handle_new_env(self) -> Tuple[bool, bool, Dict[str, str]]:
        """Handle creation of new .env file"""
        self.utils.print_warning("WARNING: Creating new .env will require container recreation!")
        self.utils.print_warning("This means:")
        self.utils.print_warning("  • PostgreSQL volume will be removed (all database data will be lost!)")
        self.utils.print_warning("  • All passwords and keys will be regenerated")
        self.utils.print_warning("  • Containers will need to be stopped and recreated")
        self.utils.print_error("CRITICAL: If PostgreSQL has important data, it will be lost!")
        self.utils.print_info("")
        self.utils.print_info("Note: Containers will be recreated at the end of setup, after all configuration.")
        self.utils.print_info("You can review all settings before confirming container recreation.")
        
        confirm = input("Do you really want to continue? Enter 'YES' to confirm: ").strip()
        
        if confirm != "YES":
            self.utils.print_warning("Operation cancelled")
            self.utils.print_info("To update settings use LiteLLM Admin UI")
            import sys
            sys.exit(0)
        
        self.utils.print_warning("You confirmed full system recreation")
        
        backup = input("Create backup of current .env? [Y/n]: ").strip().lower()
        if backup not in NO_VALUES:
            import shutil
            from datetime import datetime
            backup_name = f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy(".env", backup_name)
                self.utils.print_success(f"Backup created: {backup_name}")
            except (OSError, IOError) as e:
                self.utils.print_warning(f"Failed to create backup: {e}")
        
        self.utils.print_success("New .env file will be created")
        self.utils.print_warning("Passwords and keys will be regenerated")
        self.utils.print_info("Containers will be recreated at the end of setup (after all configuration)")
        print()  # Empty line before next section
        
        return False, True, {}
    
    def ask_budget_profile(self, reuse_env: bool, existing_env: Dict[str, str]) -> str:
        """
        Ask user for budget profile.
        
        See docs/configuration.md#budget-profiles for budget profile details.
        """
        if reuse_env:
            return existing_env.get("BUDGET_PROFILE", BUDGET_PROFILE_TEST)
        
        self.utils.print_header("💰 Budget Profile Selection")
        self.utils.print_info("Budget profile determines spending limits for models:")
        self.utils.print_info("  [1] Test - minimal limits (recommended for test environment)")
        self.utils.print_info("      • Expensive models: $1/month")
        self.utils.print_info("      • Cheap models: $10/month")
        self.utils.print_info("      • Total budget: $15/month")
        self.utils.print_info("  [2] Prod - normal limits (for production)")
        self.utils.print_info("      • Expensive models: $30-50/month")
        self.utils.print_info("      • Cheap models: $100/month")
        self.utils.print_info("      • Total budget: $200/month")
        self.utils.print_info("  [3] Unlimited - no limits (be careful!)")
        self.utils.print_info("      • Total budget: $1000/month")
        
        while True:
            choice = input("Select budget profile [1-3, Enter for test]: ").strip()
            if not choice or choice == "1":
                self.utils.print_success("Selected profile: test (minimal limits)")
                return BUDGET_PROFILE_TEST
            elif choice == "2":
                self.utils.print_success("Selected profile: prod (normal limits)")
                return "prod"
            elif choice == "3":
                self.utils.print_warning("Selected profile: unlimited (no limits)")
                self.utils.print_warning("Make sure you have control over expenses!")
                return "unlimited"
            else:
                self.utils.print_error("Select 1, 2, or 3")
    
    def ask_tavily_api_key(self, existing_env: Dict[str, str]) -> Optional[str]:
        """Ask user for Tavily API key with instructions"""
        print()
        self.utils.print_header("🔍 Web Search Configuration (Tavily)")
        print()
        self.utils.print_info("Tavily API provides web search with low CPU usage (~20-30% vs ~238% for DDGS)")
        print()
        self.utils.print_info("To get a free Tavily API key:")
        self.utils.print_info("  1. Visit: https://tavily.com/")
        self.utils.print_info("  2. Sign up for a free account")
        self.utils.print_info("  3. Get your API key from the dashboard")
        self.utils.print_info("  4. Free tier: 1000 searches/month")
        print()
        
        # Check if key already exists
        existing_key = existing_env.get("TAVILY_API_KEY", "").strip()
        if existing_key:
            masked = existing_key[:8] + "..." + existing_key[-4:] if len(existing_key) > 12 else "***"
            self.utils.print_info(f"Found existing Tavily API key: {masked}")
            print()
            choice = input(f"{self.utils.Colors.BLUE}Use existing key? (Y/n): {self.utils.Colors.RESET}").strip().lower()
            if not choice or choice in YES_VALUES:
                return existing_key
            print()
        
        # Ask if user wants to enter key now
        self.utils.print_info("Options:")
        self.utils.print_info("  [1] Enter Tavily API key now (recommended)")
        self.utils.print_info("  [2] Skip - configure later in .env file (web search disabled until then)")
        print()
        
        while True:
            choice = input(f"{self.utils.Colors.BLUE}Select option [1-2, Enter for 2]: {self.utils.Colors.RESET}").strip()
            
            if not choice or choice == "2":
                self.utils.print_info("Skipping Tavily API key configuration for now")
                self.utils.print_info("Web search will stay disabled until you add TAVILY_API_KEY to .env")
                return None
            elif choice == "1":
                print()
                self.utils.print_info("Enter your Tavily API key:")
                self.utils.print_warning("Input will be hidden for security")
                import getpass
                api_key = getpass.getpass(f"{self.utils.Colors.BLUE}Tavily API Key: {self.utils.Colors.RESET}").strip()
                
                if not api_key:
                    self.utils.print_error("API key cannot be empty")
                    continue
                
                if len(api_key) < 10:
                    self.utils.print_warning("API key seems too short. Please verify it's correct.")
                    confirm = input(f"{self.utils.Colors.BLUE}Continue anyway? (y/N): {self.utils.Colors.RESET}").strip().lower()
                    if confirm not in YES_VALUES:
                        continue
                
                self.utils.print_success(f"✅ Tavily API key saved")
                return api_key
            else:
                self.utils.print_error("Please select 1 or 2")
    
    def ask_systemd_installation(self) -> bool:
        """
        Ask user if they want to install systemd service.
        
        See docs/administration/systemd.md#installation for systemd installation details.
        """
        from ..platform_utils import detect_platform, PlatformType
        
        # Only for Linux
        platform = detect_platform()
        if platform != PlatformType.LINUX:
            return False
        
        print()
        self.utils.print_header("⚙️  Systemd Service Setup")
        print()
        self.utils.print_info("Would you like to set up AI Gateway as a systemd user service?")
        print()
        self.utils.print_info("Benefits:")
        self.utils.print_info("  ✅ Automatic startup on system boot")
        self.utils.print_info("  ✅ Runs in background even after SSH logout")
        self.utils.print_info("  ✅ Automatic restart on failures")
        self.utils.print_info("  ✅ Centralized logging via journalctl")
        print()
        self.utils.print_info("You can manage it later with:")
        self.utils.print_info("  systemctl --user start/stop/restart ai-gateway.service")
        print()
        
        while True:
            choice = input(f"{self.utils.Colors.BLUE}Install systemd service? (Y/n): {self.utils.Colors.RESET}").strip().lower()
            
            if not choice or choice in YES_VALUES:
                return True
            elif choice in NO_VALUES:
                self.utils.print_info("Skipping systemd service installation")
                self.utils.print_info("You can use ./start.sh and ./stop.sh scripts manually")
                return False
            else:
                self.utils.print_error("Please answer Y or n")


class DockerManager:
    """Docker container management"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.docker_client = DockerClient()
        self.utils = self._import_utils()
    
    def _import_utils(self):
        """Import utility functions"""
        from types import SimpleNamespace
        from ..utils import print_info, print_warning, print_success, print_error
        return SimpleNamespace(
            print_info=print_info,
            print_warning=print_warning,
            print_success=print_success,
            print_error=print_error,
        )
    
    def handle_containers(
        self,
        reuse_env: bool,
        force_recreate: bool,
        postgres_password: str
    ) -> bool:
        """
        Handle Docker containers (DEPRECATED - moved to final instructions)
        
        This method is kept for backward compatibility but is no longer called.
        Container recreation is now handled at the end of setup in _print_final_instructions.
        
        Returns:
            True if containers were started automatically
        """
        # This method is deprecated - container recreation is now handled at the end
        # Keeping for backward compatibility but should not be called
        if reuse_env and not force_recreate:
            self.utils.print_info("Using existing .env - containers will not be recreated")
            self.utils.print_info("To apply changes, restart containers manually:")
            self.utils.print_info("   docker compose restart litellm")
            print()  # Empty line for consistency
            return False
        
        # For force_recreate, this should not be called anymore
        # Container recreation is handled in _print_final_instructions
        return False
    
    def _recreate_containers(self, force_recreate: bool, postgres_password: str) -> bool:
        """Recreate Docker containers"""
        import time
        
        # Stop containers
        self.utils.print_info("Stopping containers...")
        try:
            self.docker_client.compose_down(str(self.project_root))
            self.utils.print_success("Containers stopped")
        except Exception as e:
            self.utils.print_warning(f"Error stopping containers: {e}")
            return False
        
        time.sleep(2)
        
        # Handle PostgreSQL volume if needed
        if force_recreate:
            self._remove_postgres_volume()
        
        print()  # Empty line before prompt
        
        # Ask user if they want to start containers
        if force_recreate:
            self.utils.print_info("Containers stopped and PostgreSQL volume removed.")
            self.utils.print_info("New configuration is ready. Start containers with new settings?")
        else:
            self.utils.print_info("Containers stopped. Start containers now?")
        
        start_now = input("Start containers now? [Y/n]: ").strip().lower()
        if start_now in NO_VALUES:
            self.utils.print_info("Containers will not be started.")
            self.utils.print_info("Start them later with:")
            self.utils.print_info("   ./start.sh  # Linux/macOS")
            self.utils.print_info("   start.bat  # Windows")
            print()  # Empty line for consistency
            return False
        
        # Start containers using StartService
        from .start_service import StartService
        start_service = StartService(self.project_root)
        
        if start_service.start_containers(wait_for_healthy=True):
            print()  # Empty line for consistency
            return True
        else:
            self.utils.print_warning("Containers may not be fully ready")
            self.utils.print_info("Start manually:")
            self.utils.print_info("   ./start.sh  # Linux/macOS")
            self.utils.print_info("   start.bat  # Windows")
            print()  # Empty line for consistency
            return False
    
    def _print_docker_start_instructions(self) -> None:
        """Print instructions for starting Docker daemon"""
        from ..platform_utils import detect_platform, PlatformType
        
        current_platform = detect_platform()
        
        self.utils.print_info("To start Docker daemon:")
        print()  # Empty line
        
        if current_platform == PlatformType.LINUX:
            self.utils.print_info("For rootless Docker (recommended, more secure):")
            print("  1. If rootless Docker is not initialized:")
            print("     dockerd-rootless-setuptool.sh install")
            print("     # This will initialize and automatically start the daemon")
            print()
            print("  2. If rootless Docker is already initialized but daemon is not running:")
            print("     systemctl --user start docker")
            print("     systemctl --user enable docker  # Enable auto-start on login")
            print()
            self.utils.print_info("For system-wide Docker (requires sudo):")
            print("  sudo systemctl start docker")
            print("  sudo systemctl enable docker  # Enable auto-start on boot")
        elif current_platform == PlatformType.MACOS:
            print("  Start Docker Desktop from Applications")
            print("  Or via command line:")
            print("    open -a Docker")
        elif current_platform == PlatformType.WINDOWS:
            print("  Start Docker Desktop from Start menu")
            print("  Or check that Docker Desktop is running in system tray")
            print()
            print("  If using WSL2:")
            print("    wsl")
            print("    sudo service docker start")
        else:
            print("  Please start Docker daemon for your platform")
        
        print()  # Empty line for consistency
        self.utils.print_info("After starting Docker, you can:")
        print("  • Run setup again: ./setup.sh")
        print("  • Or start containers manually: ./start.sh")
        print()  # Empty line for consistency
    
    def _remove_postgres_volume(self) -> None:
        """Remove PostgreSQL volume if it exists"""
        import subprocess
        try:
            result = subprocess.run(
                ["docker", "volume", "ls", "--filter", "name=ai-gateway_postgres_data", "--format", "{{.Name}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip():
                self.utils.print_info("New .env file was generated, removing PostgreSQL volume...")
                rm_result = subprocess.run(
                    ["docker", "volume", "rm", "ai-gateway_postgres_data"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False
                )
                if rm_result.returncode == 0:
                    self.utils.print_success("PostgreSQL volume removed")
                else:
                    self.utils.print_warning(f"Failed to remove volume: {rm_result.stderr.strip()}")
        except Exception as e:
            self.utils.print_warning(f"Error working with volume: {e}")


class SetupService:
    """
    Main setup service.
    
    See docs/getting-started.md#step-1-run-setup-script for details.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config_service = ConfigService(project_root)
        self.interactive = InteractiveSetup(project_root)
        self.docker_manager = DockerManager(project_root)
        self.utils = self._import_utils()
    
    def _import_utils(self):
        """Import utility functions"""
        from types import SimpleNamespace
        from ..utils import (
            print_header, print_info, print_success, print_warning,
            print_error, Colors, check_root, get_user, read_env_file
        )
        # Create a simple namespace with functions as attributes
        # Functions are stored directly, so they won't receive 'self' when called
        return SimpleNamespace(
            print_header=print_header,
            print_info=print_info,
            print_success=print_success,
            print_warning=print_warning,
            print_error=print_error,
            Colors=Colors,
            check_root=check_root,
            get_user=get_user,
            read_env_file=read_env_file,
        )
    
    def run_setup(self) -> None:
        """Run complete setup process"""
        from ..script_init import init_script, ScriptType
        from ..platform_utils import detect_platform, PlatformType
        from ..config import select_resource_profile, ResourceProfile
        from ..ports import configure_ports
        from ..env_generator import generate_env_file
        from ..config_generator import generate_config_yaml
        from ..docker_compose import generate_docker_compose_override
        from ..nginx import generate_nginx_config
        import os
        
        # Initialize script
        script_init = init_script("AI Gateway - Setup", ScriptType.SETUP, "🚀")
        
        # Platform checks
        current_platform = detect_platform()
        self.utils.print_info(f"Platform: {current_platform.value}")
        
        if current_platform != PlatformType.WINDOWS:
            self.utils.check_root()
            self.utils.print_success(f"Running as user: {self.utils.get_user()}")
        
        # Standard checks
        if not script_init.run_standard_checks():
            self.utils.print_error("Dependency check failed")
            import sys
            sys.exit(1)
        
        print()  # Empty line for readability
        
        # Interactive setup
        reuse_env, force_recreate, existing_env = self.interactive.ask_env_mode()
        
        # Resource profile
        if reuse_env:
            self.utils.print_info("Update mode: skipping resource profile selection")
            profile = ResourceProfile.MEDIUM_VPS
        else:
            profile = select_resource_profile()
            # Only set profile if it's not None (None means "don't configure workers")
            if profile is not None:
                self.config_service.set_resource_profile(profile)
        
        # Budget profile
        budget_profile = self.interactive.ask_budget_profile(reuse_env, existing_env)
        self.config_service.set_budget_profile(BudgetProfile(budget_profile))
        
        # Tavily API key configuration (for web search)
        if not reuse_env:
            # Only ask on new setup, not when reusing existing .env
            tavily_api_key = self.interactive.ask_tavily_api_key(existing_env)
            if tavily_api_key:
                # Save to existing_env so it gets written to .env
                existing_env["TAVILY_API_KEY"] = tavily_api_key
                self.utils.print_success("Tavily API key will be saved to .env")
        
        # Port configuration
        if reuse_env:
            self.config_service.load_from_env()
            port_config = self.config_service.get_config().port_config.to_dict()
            self.utils.print_info("Update mode: skipping port configuration")
        else:
            port_config = configure_ports()
            port_config['budget_profile'] = budget_profile  # Keep for generate_config_yaml
            # Create PortConfig without budget_profile (it's not part of PortConfig)
            port_config_for_obj = {k: v for k, v in port_config.items() if k != 'budget_profile'}
            self.config_service.set_port_config(PortConfig.from_dict(port_config_for_obj))
        
        # Generate secrets
        self.config_service.generate_secrets(reuse_existing=reuse_env)
        config = self.config_service.get_config()
        
        # Save Tavily API key if provided (before generating .env)
        if not reuse_env and "TAVILY_API_KEY" in existing_env:
            # The key will be included when generate_env_file is called
            pass
        
        if reuse_env:
            # Update mode: only regenerate config.yaml if budget profile changed
            self.utils.print_header("📝 Updating config.yaml")
            print()  # Empty line after header
            os.environ["BUDGET_PROFILE"] = budget_profile
            generate_config_yaml(budget_profile)
            
            # Also regenerate docker-compose.override.yml to ensure port mappings are correct
            # This is important when LITELLM_EXTERNAL_PORT is set in .env
            self.utils.print_header("📝 Updating docker-compose.override.yml")
            print()  # Empty line after header
            generate_docker_compose_override(
                profile=profile,
                port_config=port_config,
                selected_models=[],
            )
            
            # Update OpenWebUI web search settings if container is running
            self._update_openwebui_settings_if_running()
            
            # Nginx config - regenerate if nginx is enabled
            if port_config.get('use_nginx'):
                self.utils.print_header("📝 Updating nginx configuration")
                print()  # Empty line after header
                generate_nginx_config(port_config)
        else:
            # New setup: generate all files
            self.utils.print_header("📝 Generating config.yaml")
            print()  # Empty line after header
            os.environ["BUDGET_PROFILE"] = budget_profile
            generate_config_yaml(budget_profile)
            
            self.utils.print_header("📝 Creating .env file")
            print()  # Empty line after header
            generate_env_file(
                master_key=config.master_key or "",
                ui_password=config.ui_password or "",
                postgres_password=config.postgres_password or "",
                postgres_port=port_config['postgres_port'],
                port_config=port_config,
                webui_secret=config.webui_secret or "",
                ui_username=config.ui_username,
                preserve_first_run=True,  # Preserve FIRST_RUN flag in update mode
            )
            
            # If Tavily API key was provided, add it to .env (for both new setup and update mode)
            if "TAVILY_API_KEY" in existing_env:
                env_file = self.project_root / ".env"
                if env_file.exists():
                    content = env_file.read_text(encoding="utf-8")
                    lines = content.split('\n')
                    new_lines = []
                    key_added = False
                    
                    for line in lines:
                        if line.startswith("TAVILY_API_KEY="):
                            new_lines.append(f"TAVILY_API_KEY={existing_env['TAVILY_API_KEY']}")
                            key_added = True
                        else:
                            new_lines.append(line)
                    
                    if not key_added:
                        # Find the line with WEB_SEARCH_ENGINE and add after it
                        web_search_found = False
                        for i, line in enumerate(new_lines):
                            if line.startswith("WEB_SEARCH_ENGINE="):
                                new_lines.insert(i + 1, f"TAVILY_API_KEY={existing_env['TAVILY_API_KEY']}")
                                key_added = True
                                web_search_found = True
                                break
                        
                        # If WEB_SEARCH_ENGINE not found, add at the end of file
                        if not web_search_found:
                            new_lines.append("")
                            new_lines.append("# Tavily API Key for web search")
                            new_lines.append(f"TAVILY_API_KEY={existing_env['TAVILY_API_KEY']}")
                            key_added = True
                    
                    if key_added:
                        env_file.write_text('\n'.join(new_lines), encoding="utf-8")
                        self.utils.print_success("✅ Tavily API key saved to .env")
            
            self.utils.print_header("📝 Creating docker-compose.override.yml")
            print()  # Empty line after header
            generate_docker_compose_override(
                profile=profile,
                port_config=port_config,
                selected_models=[],
            )
            
            # Set flag to update OpenWebUI settings on next start
            # (container not running yet, so we'll update on first start)
            self._set_update_web_search_flag()
            
            # Nginx config
            if port_config.get('use_nginx'):
                self.utils.print_header("📝 Generating nginx configuration")
                print()  # Empty line after header
                generate_nginx_config(port_config)
        
        # Docker containers - handled at the end in final instructions
        # This allows user to review all settings before container recreation
        containers_started = False
        
        # Check web search configuration and warn if needed
        self._check_and_warn_web_search_config()
        
        # Final instructions (includes container recreation if needed)
        self._print_final_instructions(
            port_config, 
            profile, 
            containers_started, 
            reuse_env, 
            force_recreate,
            config.postgres_password or ""
        )
    
    def _update_openwebui_settings_if_running(self) -> None:
        """Update OpenWebUI web search settings if container is running"""
        try:
            import subprocess
            from ..infrastructure.openwebui_db import update_web_search_settings_from_env
            
            # Check if open-webui container is running
            try:
                result = subprocess.run(
                    ["docker", "ps", "--filter", "name=open-webui", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and "open-webui" in result.stdout:
                    self.utils.print_info("Updating OpenWebUI web search settings from environment variables...")
                    if update_web_search_settings_from_env("open-webui"):
                        self.utils.print_success("✅ OpenWebUI web search settings updated")
                    else:
                        self.utils.print_warning("⚠️  Could not update OpenWebUI settings (will be updated on next start)")
                        self._set_update_web_search_flag()
                else:
                    # Container not running - set flag for update on next start
                    self._set_update_web_search_flag()
            except Exception as e:
                logger.debug(f"Could not check container status: {e}")
                # Set flag for update on next start
                self._set_update_web_search_flag()
        except Exception as e:
            logger.warning(f"Error updating OpenWebUI settings: {e}")
            # Set flag for update on next start
            self._set_update_web_search_flag()
    
    def _check_and_warn_web_search_config(self) -> None:
        """Check web search configuration and warn if API key is missing"""
        try:
            env_path = self.project_root / ".env"
            if not env_path.exists():
                return
            
            env_vars = self.utils.read_env_file(self.project_root / ".env")
            web_search_engine = env_vars.get("WEB_SEARCH_ENGINE", "tavily").lower()
            tavily_api_key = env_vars.get("TAVILY_API_KEY", "").strip()
            api_key_map = {
                "tavily": ("TAVILY_API_KEY", tavily_api_key),
                "google_pse": ("GOOGLE_PSE_API_KEY", env_vars.get("GOOGLE_PSE_API_KEY", "").strip()),
                "serper": ("SERPER_API_KEY", env_vars.get("SERPER_API_KEY", "").strip()),
                "brave": ("BRAVE_API_KEY", env_vars.get("BRAVE_API_KEY", "").strip()),
                "kagi": ("KAGI_API_KEY", env_vars.get("KAGI_API_KEY", "").strip()),
            }
            supported_api_engines = set(api_key_map.keys())
            
            if web_search_engine == "tavily" and not tavily_api_key:
                self.utils.print_warning("⚠️  Web Search Configuration Warning")
                print()
                print("   Tavily API key is not configured, but WEB_SEARCH_ENGINE=tavily is set.")
                print("   Web search will not work without an API key.")
                print()
                print("   Options:")
                print("   1. Get free Tavily API key (recommended):")
                print("      - Sign up at: https://tavily.com/")
                print("      - Free tier: 1000 searches/month")
                print("      - Add to .env: TAVILY_API_KEY=your-api-key-here")
                print("      - CPU usage: ~20-30% per user (low)")
                print()
                print("   2. Disable web search until you add an API key:")
                print("      - Remove or comment out WEB_SEARCH_ENGINE in .env")
                print()
            elif web_search_engine in supported_api_engines:
                key_name, key_value = api_key_map[web_search_engine]
                if not key_value:
                    self.utils.print_warning("⚠️  Web Search Configuration Warning")
                    print()
                    print(f"   {web_search_engine} requires {key_name}, but it is not set in .env.")
                    print("   Web search will be disabled until the key is provided.")
                    print()
            else:
                self.utils.print_warning("⚠️  Web Search Configuration Warning")
                print()
                print(f"   WEB_SEARCH_ENGINE={web_search_engine} is set, but this stack no longer ships Playwright.")
                print("   Engines that only return URLs (e.g. ddgs) are unsupported out-of-the-box.")
                print()
                print("   Please switch to Tavily or another API-based provider that returns content.")
                print()
        except Exception as e:
            logger.debug(f"Error checking web search config: {e}")
    
    def _set_update_web_search_flag(self) -> None:
        """Set UPDATE_WEB_SEARCH_SETTINGS flag in .env for update on next start"""
        try:
            env_file = self.project_root / ".env"
            if not env_file.exists():
                return
            
            # Read current .env
            env_vars = self.utils.read_env_file(env_file)
            
            # Set flag
            env_vars["UPDATE_WEB_SEARCH_SETTINGS"] = "yes"
            
            # Write back to .env
            with open(env_file, 'w') as f:
                for key, value in env_vars.items():
                    # Escape special characters in value
                    if ' ' in value or '#' in value or '$' in value:
                        f.write(f'{key}="{value}"\n')
                    else:
                        f.write(f'{key}={value}\n')
            
            logger.debug("Set UPDATE_WEB_SEARCH_SETTINGS flag in .env")
        except Exception as e:
            logger.warning(f"Could not set UPDATE_WEB_SEARCH_SETTINGS flag: {e}")
    
    def _print_final_instructions(
        self, 
        port_config: Dict, 
        profile: ResourceProfile, 
        containers_started: bool, 
        reuse_env: bool,
        force_recreate: bool,
        postgres_password: str
    ) -> None:
        """Print final setup instructions and handle container recreation"""
        # Quick setup mode (reuse_env=True, force_recreate=False): skip container recreation
        # No need to recreate containers or ask user - just update config files
        if reuse_env and not force_recreate:
            self.utils.print_header("✅ Update Complete!")
            self.utils.print_info("Configuration updated successfully.")
            self.utils.print_info("All settings are managed through LiteLLM Admin UI")
            print()  # Empty line
            self.utils.print_info("To apply changes, restart containers if needed:")
            self.utils.print_info("   docker compose restart litellm")
            
            # Ask about systemd service installation (Linux only) - even in update mode
            if self.interactive.ask_systemd_installation():
                self._install_systemd_service()
            
            # Exit early - no container recreation in quick setup mode
            return
        else:
            # New setup or force recreate: full instructions
            self.utils.print_header("✅ Setup Complete!")
            self.utils.print_info("All configuration files have been generated.")
            print()  # Empty line
            
            # Handle container recreation at the end
            if force_recreate:
                self.utils.print_header("🐳 Container Recreation Required")
                self.utils.print_warning("New .env file was created with new passwords.")
                self.utils.print_warning("PostgreSQL volume needs to be removed and containers recreated.")
                self.utils.print_error("WARNING: This will delete all PostgreSQL data!")
                print()  # Empty line
                
                # Show LiteLLM Admin UI credentials for convenience
                env_vars = self.utils.read_env_file(self.project_root / ".env")
                ui_username = env_vars.get("UI_USERNAME", "admin").strip()
                ui_password = env_vars.get("UI_PASSWORD", "").strip()
                
                if ui_username and ui_password:
                    print()
                    self.utils.print_info("🔑 LiteLLM Admin UI Credentials:")
                    print()
                    print(f"  Username: {self.utils.Colors.GREEN}{ui_username}{self.utils.Colors.RESET}")
                    print(f"  Password: {self.utils.Colors.GREEN}{ui_password}{self.utils.Colors.RESET}")
                    print()
                    if port_config.get('use_nginx'):
                        litellm_ui_port = port_config.get('litellm_external_port', '')
                        if litellm_ui_port:
                            self.utils.print_info(f"  Access: http://YOUR_IP:{litellm_ui_port}/ui")
                    else:
                        litellm_port = port_config.get('litellm_external_port', 4000)
                        self.utils.print_info(f"  Access: http://YOUR_IP:{litellm_port}/ui")
                    print()
                    self.utils.print_warning("⚠️  Save these credentials - they won't be shown again!")
                    print()
                
                # Check Docker availability
                if not self.docker_manager.docker_client.check_available()[0]:
                    self.utils.print_warning("Docker is not available or not running")
                    self.utils.print_info("Start Docker and run ./start.sh to recreate containers")
                    return
                
                if not self.docker_manager.docker_client.check_daemon_running():
                    self.utils.print_warning("Docker daemon is not running")
                    self.docker_manager._print_docker_start_instructions()
                    return
                
                # Ask for confirmation before recreation
                print()  # Empty line before prompt
                choice = input("Recreate containers now? [Y/n]: ").strip().lower()
                
                if choice in NO_VALUES:
                    self.utils.print_info("Containers will not be recreated now.")
                    self.utils.print_info("To recreate containers later:")
                    self.utils.print_info("   ./start.sh  # Linux/macOS")
                    self.utils.print_info("   start.bat  # Windows")
                    print()  # Empty line
                    self.utils.print_info("Note: PostgreSQL volume will be removed on first start.")
                else:
                    # Recreate containers now
                    containers_started = self.docker_manager._recreate_containers(
                        force_recreate=True,
                        postgres_password=postgres_password
                    )
            else:
                # New setup without force recreate
                self.utils.print_info("Next steps:")
                self.utils.print_info("   1. Start the system: ./start.sh (or start.bat on Windows)")
                self.utils.print_info("   2. Access URLs will be shown after containers start")
                self.utils.print_info("   3. Configure providers, API keys and models through LiteLLM Admin UI")
            
            # Final status
            if containers_started:
                self.utils.print_header("🚀 System Started!")
                self.utils.print_success("Containers are running!")
                self.utils.print_info("Wait 30-60 seconds for LiteLLM and Open WebUI to fully initialize.")
                
                # Show LiteLLM Admin UI credentials for convenience (on first setup or force_recreate)
                env_vars = self.utils.read_env_file(self.project_root / ".env")
                first_run = env_vars.get("FIRST_RUN", "no").lower() in ("yes", "true", "1")
                
                if first_run or force_recreate:
                    ui_username = env_vars.get("UI_USERNAME", "admin").strip()
                    ui_password = env_vars.get("UI_PASSWORD", "").strip()
                    
                    if ui_username and ui_password:
                        print()
                        self.utils.print_info("🔑 LiteLLM Admin UI Credentials:")
                        print()
                        print(f"  Username: {self.utils.Colors.GREEN}{ui_username}{self.utils.Colors.RESET}")
                        print(f"  Password: {self.utils.Colors.GREEN}{ui_password}{self.utils.Colors.RESET}")
                        print()
                        if port_config.get('use_nginx'):
                            litellm_ui_port = port_config.get('litellm_external_port', '')
                            if litellm_ui_port:
                                self.utils.print_info(f"  Access: http://YOUR_IP:{litellm_ui_port}/ui")
                        else:
                            litellm_port = port_config.get('litellm_external_port', 4000)
                            self.utils.print_info(f"  Access: http://YOUR_IP:{litellm_port}/ui")
                        print()
                        self.utils.print_warning("⚠️  Save these credentials - they won't be shown again!")
                        print()
                
                # Check if this is first run and Virtual Key needs to be created
                virtual_key = env_vars.get("VIRTUAL_KEY", "").strip()
                
                if not virtual_key and first_run:
                    # Wait for LiteLLM to be ready, then create Virtual Key automatically
                    print()
                    self.utils.print_info("🔑 Creating Virtual Key automatically...")
                    self.utils.print_info("Waiting for LiteLLM to be ready...")
                    
                    import time
                    time.sleep(45)  # Wait for LiteLLM to fully start
                    
                    # Try to create Virtual Key
                    from ..virtual_key import run_inside_docker_container
                    master_key = env_vars.get("LITELLM_MASTER_KEY", "").strip()
                    
                    if master_key:
                        virtual_key = run_inside_docker_container(self.project_root, master_key)
                        
                        if virtual_key:
                            # Save Virtual Key to .env
                            env_file = self.project_root / ".env"
                            content = env_file.read_text(encoding="utf-8")
                            
                            # Update or add VIRTUAL_KEY
                            lines = content.split('\n')
                            new_lines = []
                            virtual_key_added = False
                            
                            for line in lines:
                                if line.startswith("VIRTUAL_KEY="):
                                    new_lines.append(f"VIRTUAL_KEY={virtual_key}")
                                    virtual_key_added = True
                                elif line.strip().startswith("# Virtual Key") and not virtual_key_added:
                                    # Add Virtual Key after comment
                                    new_lines.append(line)
                                    new_lines.append(f"VIRTUAL_KEY={virtual_key}")
                                    virtual_key_added = True
                                else:
                                    new_lines.append(line)
                            
                            if not virtual_key_added:
                                # Add at the end
                                new_lines.append("")
                                new_lines.append("# Virtual Key for Open WebUI (auto-created during setup)")
                                new_lines.append(f"VIRTUAL_KEY={virtual_key}")
                            
                            env_file.write_text('\n'.join(new_lines), encoding="utf-8")
                            
                            # Update FIRST_RUN flag
                            content = env_file.read_text(encoding="utf-8")
                            content = content.replace("FIRST_RUN=yes", "FIRST_RUN=no")
                            env_file.write_text(content, encoding="utf-8")
                            
                            self.utils.print_success(f"✅ Virtual Key created and saved to .env")
                            self.utils.print_info(f"   Key: {virtual_key[:30]}...")
                            print()
                            self.utils.print_info("💡 Open WebUI is configured to use Virtual Key automatically")
                            self.utils.print_info("   No additional configuration needed - Virtual Key is ready to use")
                            print()
                        else:
                            self.utils.print_warning("⚠️  Could not create Virtual Key automatically")
                            self.utils.print_info("   You can create it manually later:")
                            self.utils.print_info("   ./virtual-key.sh")
                            self.utils.print_info("   # Or: python3 -m src.virtual_key")
                            print()
                
                # Re-read .env to get updated Virtual Key if it was just created
                env_vars = self.utils.read_env_file(self.project_root / ".env")
                virtual_key = env_vars.get("VIRTUAL_KEY", "").strip()
                
                # Use StartService to print access info (unified logic)
                from .start_service import StartService
                start_service = StartService(self.project_root)
                start_service.print_access_info()
                
                # Show Virtual Key status
                if virtual_key:
                    print()
                    self.utils.print_success("✅ Virtual Key is configured and ready to use")
                    self.utils.print_info("   Open WebUI will use Virtual Key automatically")
                elif not first_run:
                    print()
                    self.utils.print_info("💡 Next Steps:")
                    print()
                    self.utils.print_info("1. Create Virtual Key in LiteLLM UI (recommended for security):")
                    if port_config.get('use_nginx'):
                        litellm_ui_port = port_config.get('litellm_external_port', '')
                        if litellm_ui_port:
                            self.utils.print_info(f"   • Open LiteLLM UI: http://YOUR_IP:{litellm_ui_port}/ui")
                    else:
                        litellm_port = port_config.get('litellm_external_port', 4000)
                        self.utils.print_info(f"   • Open LiteLLM UI: http://YOUR_IP:{litellm_port}/ui")
                    self.utils.print_info("   • Create Team and Virtual Key")
                    self.utils.print_info("   • Copy the Virtual Key")
                    print()
                    self.utils.print_info("   Or run setup script for interactive setup:")
                    self.utils.print_info("   python3 -m src.virtual_key")
                    print()
            else:
                self.utils.print_header("🚀 Starting System")
                self.utils.print_info("Start the system:")
                self.utils.print_info("   ./start.sh  # Linux/macOS")
                self.utils.print_info("   start.bat  # Windows")
                print()  # Empty line
                self.utils.print_info("After startup, access services:")
                # Use StartService to print access info (unified logic)
                from .start_service import StartService
                start_service = StartService(self.project_root)
                start_service.print_access_info()
                print()  # Empty line
                self.utils.print_info("   Configure providers, API keys and models through LiteLLM Admin UI")
                
                # Ask about systemd service installation (Linux only) - for new setup
                if self.interactive.ask_systemd_installation():
                    self._install_systemd_service()
    
    def _install_systemd_service(self) -> None:
        """Install and configure systemd service"""
        from ..infrastructure.systemd_service import SystemdService
        
        print()
        self.utils.print_header("📦 Installing Systemd Service")
        
        try:
            systemd = SystemdService(self.project_root)
            
            # Install service file
            self.utils.print_info("Creating service file...")
            if not systemd.install():
                self.utils.print_error("Failed to install service file")
                return
            self.utils.print_success(f"✅ Service file created: {systemd.service_file}")
            
            # Enable service
            self.utils.print_info("Enabling service autostart...")
            if not systemd.enable():
                self.utils.print_error("Failed to enable service")
                return
            self.utils.print_success("✅ Service enabled for autostart")
            
            # Enable lingering
            self.utils.print_info("Enabling lingering (allows service to run after logout)...")
            if systemd.enable_lingering():
                self.utils.print_success("✅ Lingering enabled")
            else:
                self.utils.print_warning("⚠️  Could not enable lingering (may need manual setup)")
            
            print()
            self.utils.print_success("🎉 Systemd service installed successfully!")
            print()
            self.utils.print_info("Useful commands:")
            self.utils.print_info("  systemctl --user start ai-gateway.service    # Start")
            self.utils.print_info("  systemctl --user stop ai-gateway.service     # Stop")
            self.utils.print_info("  systemctl --user restart ai-gateway.service  # Restart")
            self.utils.print_info("  systemctl --user status ai-gateway.service   # Status")
            self.utils.print_info("  journalctl --user -u ai-gateway.service -f   # View logs")
            print()
            self.utils.print_info("📚 See docs/administration/systemd.md for more information")
            print()
            
            # Ask if user wants to start now
            choice = input(f"{self.utils.Colors.BLUE}Start service now? (Y/n): {self.utils.Colors.RESET}").strip().lower()
            if not choice or choice in YES_VALUES:
                self.utils.print_info("Starting service...")
                if systemd.start():
                    self.utils.print_success("✅ Service started successfully")
                    print()
                    self.utils.print_info("Check status with:")
                    self.utils.print_info("  systemctl --user status ai-gateway.service")
                else:
                    self.utils.print_error("Failed to start service")
                    self.utils.print_info("You can start it manually with:")
                    self.utils.print_info("  systemctl --user start ai-gateway.service")
            else:
                self.utils.print_info("You can start the service later with:")
                self.utils.print_info("  systemctl --user start ai-gateway.service")
        
        except Exception as e:
            self.utils.print_error(f"Failed to install systemd service: {e}")
            self.utils.print_info("You can use ./start.sh script instead")

