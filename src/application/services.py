"""
Application services - business logic
"""

from pathlib import Path

from ..core.config import AppConfig, BudgetProfile, PortConfig, ResourceProfile
from ..infrastructure.file_repository import FileRepository
from ..infrastructure.logger import get_logger
from ..infrastructure.security import SecurityService

logger = get_logger(__name__)


class ConfigService:
    """
    Service for configuration management.

    See docs/configuration.md for detailed configuration information.
    """

    def __init__(self, project_root: Path):
        """
        Initialize config service

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.file_repo = FileRepository(self.project_root)
        self.config = AppConfig(project_root=self.project_root)

    def load_from_env(self) -> None:
        """
        Load configuration from existing .env file.

        See docs/configuration.md for configuration details.
        """
        if not self.file_repo.exists(Path(".env")):
            logger.warning(".env file not found")
            return

        env_vars = self.file_repo.read_env_file()

        # Load budget profile
        budget_str = env_vars.get("BUDGET_PROFILE", "test")
        try:
            self.config.budget_profile = BudgetProfile(budget_str)
        except ValueError:
            from ..core.constants import BUDGET_PROFILE_TEST

            logger.warning(
                f"Invalid budget profile: {budget_str}, using {BUDGET_PROFILE_TEST}"
            )
            self.config.budget_profile = BudgetProfile.TEST

        # Load security values
        self.config.master_key = env_vars.get("LITELLM_MASTER_KEY")
        self.config.ui_username = env_vars.get("UI_USERNAME", "admin")
        self.config.ui_password = env_vars.get("UI_PASSWORD")
        self.config.postgres_password = env_vars.get("POSTGRES_PASSWORD")
        self.config.webui_secret = env_vars.get("WEBUI_SECRET_KEY")

        # Load port config
        from ..core.constants import (
            DEFAULT_LITELLM_PORT,
            DEFAULT_POSTGRES_PORT,
            DEFAULT_WEBUI_INTERNAL_PORT,
            MAX_PORT,
            MIN_PORT,
        )
        from ..core.exceptions import ValidationError

        port_config = PortConfig()

        # Validate and set ports with error handling
        try:
            postgres_port = int(
                env_vars.get("POSTGRES_PORT", str(DEFAULT_POSTGRES_PORT))
            )
            if not (MIN_PORT <= postgres_port <= MAX_PORT):
                raise ValidationError(f"Invalid PostgreSQL port: {postgres_port}")
            port_config.postgres_port = postgres_port
        except ValueError as e:
            raise ValidationError(
                f"Invalid PostgreSQL port value in .env: {env_vars.get('POSTGRES_PORT')}"
            ) from e

        try:
            litellm_port = int(
                env_vars.get("LITELLM_INTERNAL_PORT", str(DEFAULT_LITELLM_PORT))
            )
            if not (MIN_PORT <= litellm_port <= MAX_PORT):
                raise ValidationError(f"Invalid LiteLLM port: {litellm_port}")
            port_config.litellm_internal_port = litellm_port
        except ValueError as e:
            raise ValidationError(
                f"Invalid LiteLLM port value in .env: {env_vars.get('LITELLM_INTERNAL_PORT')}"
            ) from e

        try:
            webui_port = int(
                env_vars.get("WEBUI_INTERNAL_PORT", str(DEFAULT_WEBUI_INTERNAL_PORT))
            )
            if not (MIN_PORT <= webui_port <= MAX_PORT):
                raise ValidationError(f"Invalid WebUI port: {webui_port}")
            port_config.webui_internal_port = webui_port
        except ValueError as e:
            raise ValidationError(
                f"Invalid WebUI port value in .env: {env_vars.get('WEBUI_INTERNAL_PORT')}"
            ) from e

        # External ports
        litellm_ext = env_vars.get("LITELLM_EXTERNAL_PORT", "").strip()
        if litellm_ext:
            try:
                port_config.litellm_external_port = int(litellm_ext)
            except ValueError as e:
                raise ValidationError(
                    f"Invalid LiteLLM external port value in .env: {litellm_ext}"
                ) from e
        else:
            port_config.litellm_external_port = None

        webui_ext = env_vars.get("WEBUI_EXTERNAL_PORT", "").strip()
        if webui_ext:
            try:
                port_config.webui_external_port = int(webui_ext)
            except ValueError as e:
                raise ValidationError(
                    f"Invalid WebUI external port value in .env: {webui_ext}"
                ) from e
        else:
            port_config.webui_external_port = None

        # Nginx settings
        port_config.use_nginx = env_vars.get("USE_NGINX", "").lower() in (
            "yes",
            "true",
            "1",
        )
        # SSL configuration removed - users should configure via their own nginx
        port_config.use_ssl = False
        port_config.ssl_domain = None

        nginx_http = env_vars.get("NGINX_HTTP_PORT", "").strip()
        if nginx_http:
            try:
                port_config.nginx_http_port = int(nginx_http)
            except ValueError as e:
                raise ValidationError(
                    f"Invalid Nginx HTTP port value in .env: {nginx_http}"
                ) from e
        else:
            port_config.nginx_http_port = None

        nginx_https = env_vars.get("NGINX_HTTPS_PORT", "").strip()
        if nginx_https and nginx_https.lower() != "none":
            try:
                port_config.nginx_https_port = int(nginx_https)
            except ValueError as e:
                raise ValidationError(
                    f"Invalid Nginx HTTPS port value in .env: {nginx_https}"
                ) from e
        else:
            port_config.nginx_https_port = None

        nginx_port = env_vars.get("NGINX_PORT", "").strip()
        if nginx_port and nginx_port.lower() != "none":
            try:
                port_config.nginx_port = int(nginx_port)
            except ValueError as e:
                raise ValidationError(
                    f"Invalid Nginx port value in .env: {nginx_port}"
                ) from e
        else:
            port_config.nginx_port = None

        self.config.port_config = port_config

        logger.info("Configuration loaded from .env")

    def generate_secrets(self, reuse_existing: bool = True) -> None:
        """
        Generate security secrets.

        See docs/security.md for security best practices.

        Args:
            reuse_existing: Reuse existing secrets from .env if available
        """
        security = SecurityService()

        if reuse_existing:
            self.load_from_env()

        # Generate master key if not present
        if not self.config.master_key:
            self.config.master_key = security.generate_master_key()
            logger.info("Generated new master key")

        # Generate passwords if not present
        if not self.config.ui_password:
            self.config.ui_password = security.generate_password(16)
            logger.info("Generated new UI password")

        if not self.config.postgres_password:
            self.config.postgres_password = security.generate_password(32)
            logger.info("Generated new PostgreSQL password")

        if not self.config.webui_secret:
            self.config.webui_secret = security.generate_password(32)
            logger.info("Generated new WebUI secret")

    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self.config

    def set_resource_profile(self, profile: ResourceProfile) -> None:
        """Set resource profile"""
        self.config.resource_profile = profile
        logger.info(f"Resource profile set to {profile.value}")

    def set_budget_profile(self, profile: BudgetProfile) -> None:
        """Set budget profile"""
        self.config.budget_profile = profile
        logger.info(f"Budget profile set to {profile.value}")

    def set_port_config(self, port_config: PortConfig) -> None:
        """Set port configuration"""
        self.config.port_config = port_config
        logger.info("Port configuration updated")

    def get_env_value(self, key: str, default: str = "") -> str:
        """
        Get value from .env file

        Args:
            key: Environment variable key
            default: Default value if key not found

        Returns:
            Value from .env or default
        """
        if not self.file_repo.exists(Path(".env")):
            return default

        env_vars = self.file_repo.read_env_file()
        return env_vars.get(key, default).strip()

    def get_virtual_key(self) -> str:
        """
        Get Virtual Key from .env.

        See docs/configuration/virtual-key.md for Virtual Key details.

        Returns:
            Virtual Key string or empty string if not found
        """
        return self.get_env_value("VIRTUAL_KEY", "")

    def is_first_run(self) -> bool:
        """Check if this is first run"""
        first_run = self.get_env_value("FIRST_RUN", "no").lower()
        return first_run in ("yes", "true", "1")

    def should_update_web_search_settings(self) -> bool:
        """Check if web search settings should be updated"""
        update_flag = self.get_env_value("UPDATE_WEB_SEARCH_SETTINGS", "no").lower()
        return update_flag in ("yes", "true", "1")

    def get_master_key(self) -> str:
        """
        Get Master Key from .env.

        See docs/security.md for security details.

        Returns:
            Master Key string or empty string if not found
        """
        return self.get_env_value("LITELLM_MASTER_KEY", "")
