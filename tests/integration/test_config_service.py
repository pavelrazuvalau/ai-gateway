"""
Integration tests for ConfigService.

See docs/configuration.md for configuration details.
"""

from pathlib import Path

import pytest

from src.application.services import ConfigService
from src.core.config import AppConfig, BudgetProfile, PortConfig, ResourceProfile
from src.core.constants import (
    DEFAULT_LITELLM_PORT,
    DEFAULT_POSTGRES_PORT,
    DEFAULT_UI_USERNAME,
    DEFAULT_WEBUI_INTERNAL_PORT,
    MAX_PORT,
    MIN_PORT,
)
from src.core.exceptions import ValidationError


class TestConfigServiceInit:
    """Test ConfigService initialization."""

    def test_init_creates_service(self, project_root: Path):
        """Test that ConfigService initializes correctly."""
        service = ConfigService(project_root)
        assert service.project_root == project_root
        assert isinstance(service.config, AppConfig)
        assert service.config.project_root == project_root

    def test_init_with_default_config(self, project_root: Path):
        """Test that ConfigService uses default AppConfig values."""
        service = ConfigService(project_root)
        config = service.get_config()
        assert config.resource_profile == ResourceProfile.MEDIUM_VPS
        assert config.budget_profile == BudgetProfile.TEST
        assert config.ui_username == DEFAULT_UI_USERNAME


class TestConfigServiceLoadFromEnv:
    """Test loading configuration from .env file.

    See docs/configuration.md#environment-variables-reference for env var details.
    """

    def test_load_from_env_file_not_found(self, project_root: Path):
        """Test loading when .env file doesn't exist."""
        service = ConfigService(project_root)
        # Should not raise exception, just log warning
        service.load_from_env()
        config = service.get_config()
        # Should keep default values
        assert config.budget_profile == BudgetProfile.TEST

    def test_load_from_env_budget_profile(self, project_root: Path):
        """Test loading budget profile from .env."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        # Create .env with budget profile
        env_content = "BUDGET_PROFILE=prod\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        assert config.budget_profile == BudgetProfile.PROD

    def test_load_from_env_budget_profile_invalid(self, project_root: Path):
        """Test loading invalid budget profile falls back to test."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        # Create .env with invalid budget profile
        env_content = "BUDGET_PROFILE=invalid\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        # Should fall back to TEST
        assert config.budget_profile == BudgetProfile.TEST

    def test_load_from_env_security_values(self, project_root: Path):
        """Test loading security values from .env."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = """LITELLM_MASTER_KEY=sk-test-master-key
UI_USERNAME=custom_admin
UI_PASSWORD=test_password_123
POSTGRES_PASSWORD=postgres_pass_456
WEBUI_SECRET_KEY=webui_secret_789
"""
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        assert config.master_key == "sk-test-master-key"
        assert config.ui_username == "custom_admin"
        assert config.ui_password == "test_password_123"
        assert config.postgres_password == "postgres_pass_456"
        assert config.webui_secret == "webui_secret_789"

    def test_load_from_env_ui_username_default(self, project_root: Path):
        """Test that UI_USERNAME defaults to 'admin' if not set."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "LITELLM_MASTER_KEY=sk-test\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        assert config.ui_username == DEFAULT_UI_USERNAME

    def test_load_from_env_ports_defaults(self, project_root: Path):
        """Test loading ports with default values.

        See docs/configuration.md#port-configuration for default ports.
        """
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "LITELLM_MASTER_KEY=sk-test\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        # Check default ports match documentation
        assert port_config.postgres_port == DEFAULT_POSTGRES_PORT
        assert port_config.litellm_internal_port == DEFAULT_LITELLM_PORT
        assert port_config.webui_internal_port == DEFAULT_WEBUI_INTERNAL_PORT

    def test_load_from_env_ports_custom(self, project_root: Path):
        """Test loading custom ports from .env."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = """POSTGRES_PORT=5433
LITELLM_INTERNAL_PORT=4001
WEBUI_INTERNAL_PORT=8081
"""
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        assert port_config.postgres_port == 5433
        assert port_config.litellm_internal_port == 4001
        assert port_config.webui_internal_port == 8081

    def test_load_from_env_ports_external(self, project_root: Path):
        """Test loading external ports from .env."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = """LITELLM_EXTERNAL_PORT=5000
WEBUI_EXTERNAL_PORT=3001
"""
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        assert port_config.litellm_external_port == 5000
        assert port_config.webui_external_port == 3001

    def test_load_from_env_ports_external_empty(self, project_root: Path):
        """Test that empty external ports are set to None."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "LITELLM_EXTERNAL_PORT=\nWEBUI_EXTERNAL_PORT=\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        assert port_config.litellm_external_port is None
        assert port_config.webui_external_port is None

    def test_load_from_env_port_invalid_value(self, project_root: Path):
        """Test that invalid port values raise ValidationError."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "POSTGRES_PORT=invalid\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        with pytest.raises(ValidationError, match="Invalid PostgreSQL port value"):
            service.load_from_env()

    def test_load_from_env_port_out_of_range_low(self, project_root: Path):
        """Test that ports below MIN_PORT raise ValidationError."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = f"POSTGRES_PORT={MIN_PORT - 1}\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        with pytest.raises(ValidationError, match="Invalid PostgreSQL port"):
            service.load_from_env()

    def test_load_from_env_port_out_of_range_high(self, project_root: Path):
        """Test that ports above MAX_PORT raise ValidationError."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = f"POSTGRES_PORT={MAX_PORT + 1}\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        with pytest.raises(ValidationError, match="Invalid PostgreSQL port"):
            service.load_from_env()

    def test_load_from_env_nginx_enabled(self, project_root: Path):
        """Test loading Nginx configuration from .env."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = """USE_NGINX=yes
NGINX_HTTP_PORT=8080
NGINX_HTTPS_PORT=8443
NGINX_PORT=80
"""
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        assert port_config.use_nginx is True
        assert port_config.nginx_http_port == 8080
        assert port_config.nginx_https_port == 8443
        assert port_config.nginx_port == 80

    def test_load_from_env_nginx_disabled(self, project_root: Path):
        """Test that Nginx is disabled when USE_NGINX is not 'yes'."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "USE_NGINX=no\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        assert port_config.use_nginx is False

    def test_load_from_env_nginx_https_none(self, project_root: Path):
        """Test that NGINX_HTTPS_PORT='none' sets port to None."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "NGINX_HTTPS_PORT=none\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        assert port_config.nginx_https_port is None

    def test_load_from_env_ssl_disabled(self, project_root: Path):
        """Test that SSL is always disabled (users configure via external nginx)."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "USE_NGINX=yes\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.load_from_env()
        config = service.get_config()
        port_config = config.port_config

        assert port_config.use_ssl is False
        assert port_config.ssl_domain is None


class TestConfigServiceGenerateSecrets:
    """Test secret generation in ConfigService.

    See docs/security.md for security details.
    """

    def test_generate_secrets_new(self, project_root: Path):
        """Test generating new secrets when none exist."""
        service = ConfigService(project_root)
        service.generate_secrets(reuse_existing=False)

        config = service.get_config()
        assert config.master_key is not None
        assert config.master_key.startswith("sk-")
        assert config.ui_password is not None
        assert len(config.ui_password) == 16
        assert config.postgres_password is not None
        assert len(config.postgres_password) == 32
        assert config.webui_secret is not None
        assert len(config.webui_secret) == 32

    def test_generate_secrets_reuse_existing(self, project_root: Path):
        """Test that existing secrets are reused when reuse_existing=True."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        # Create .env with existing secrets
        env_content = """LITELLM_MASTER_KEY=sk-existing-master-key
UI_PASSWORD=existing_ui_password
POSTGRES_PASSWORD=existing_postgres_password
WEBUI_SECRET_KEY=existing_webui_secret
"""
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.generate_secrets(reuse_existing=True)

        config = service.get_config()
        assert config.master_key == "sk-existing-master-key"
        assert config.ui_password == "existing_ui_password"
        assert config.postgres_password == "existing_postgres_password"
        assert config.webui_secret == "existing_webui_secret"

    def test_generate_secrets_partial_existing(self, project_root: Path):
        """Test generating only missing secrets."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        # Create .env with only master key
        env_content = "LITELLM_MASTER_KEY=sk-existing-master-key\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        service.generate_secrets(reuse_existing=True)

        config = service.get_config()
        # Master key should be reused
        assert config.master_key == "sk-existing-master-key"
        # Other secrets should be generated
        assert config.ui_password is not None
        assert config.postgres_password is not None
        assert config.webui_secret is not None


class TestConfigServiceSetters:
    """Test setter methods in ConfigService."""

    def test_set_resource_profile(self, project_root: Path):
        """Test setting resource profile."""
        service = ConfigService(project_root)
        service.set_resource_profile(ResourceProfile.LARGE_VPS)

        config = service.get_config()
        assert config.resource_profile == ResourceProfile.LARGE_VPS

    def test_set_budget_profile(self, project_root: Path):
        """Test setting budget profile."""
        service = ConfigService(project_root)
        service.set_budget_profile(BudgetProfile.PROD)

        config = service.get_config()
        assert config.budget_profile == BudgetProfile.PROD

    def test_set_port_config(self, project_root: Path):
        """Test setting port configuration."""
        service = ConfigService(project_root)
        port_config = PortConfig(
            postgres_port=5433,
            litellm_internal_port=4001,
            webui_internal_port=8081,
        )
        service.set_port_config(port_config)

        config = service.get_config()
        assert config.port_config.postgres_port == 5433
        assert config.port_config.litellm_internal_port == 4001
        assert config.port_config.webui_internal_port == 8081


class TestConfigServiceEnvHelpers:
    """Test environment variable helper methods."""

    def test_get_env_value_existing(self, project_root: Path):
        """Test getting existing env value."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "TEST_KEY=test_value\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        value = service.get_env_value("TEST_KEY")
        assert value == "test_value"

    def test_get_env_value_missing(self, project_root: Path):
        """Test getting missing env value returns default."""
        service = ConfigService(project_root)
        value = service.get_env_value("MISSING_KEY", default="default_value")
        assert value == "default_value"

    def test_get_env_value_no_env_file(self, project_root: Path):
        """Test getting env value when .env doesn't exist."""
        service = ConfigService(project_root)
        value = service.get_env_value("ANY_KEY", default="default")
        assert value == "default"

    def test_get_env_value_strips_whitespace(self, project_root: Path):
        """Test that get_env_value strips whitespace."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "TEST_KEY=  test_value  \n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        value = service.get_env_value("TEST_KEY")
        assert value == "test_value"

    def test_get_virtual_key(self, project_root: Path):
        """Test getting Virtual Key from .env."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "VIRTUAL_KEY=sk-virtual-key-123\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        virtual_key = service.get_virtual_key()
        assert virtual_key == "sk-virtual-key-123"

    def test_get_virtual_key_missing(self, project_root: Path):
        """Test getting Virtual Key when not set."""
        service = ConfigService(project_root)
        virtual_key = service.get_virtual_key()
        assert virtual_key == ""

    def test_is_first_run_true(self, project_root: Path):
        """Test is_first_run returns True for various values."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        for value in ("yes", "true", "1"):
            env_content = f"FIRST_RUN={value}\n"
            file_repo.write_text(Path(".env"), env_content)
            file_repo.set_permissions(Path(".env"), 0o600)

            assert service.is_first_run() is True

    def test_is_first_run_false(self, project_root: Path):
        """Test is_first_run returns False for various values."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        for value in ("no", "false", "0", ""):
            env_content = f"FIRST_RUN={value}\n"
            file_repo.write_text(Path(".env"), env_content)
            file_repo.set_permissions(Path(".env"), 0o600)

            assert service.is_first_run() is False

    def test_should_update_web_search_settings_true(self, project_root: Path):
        """Test should_update_web_search_settings returns True."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        for value in ("yes", "true", "1"):
            env_content = f"UPDATE_WEB_SEARCH_SETTINGS={value}\n"
            file_repo.write_text(Path(".env"), env_content)
            file_repo.set_permissions(Path(".env"), 0o600)

            assert service.should_update_web_search_settings() is True

    def test_should_update_web_search_settings_false(self, project_root: Path):
        """Test should_update_web_search_settings returns False."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        for value in ("no", "false", "0", ""):
            env_content = f"UPDATE_WEB_SEARCH_SETTINGS={value}\n"
            file_repo.write_text(Path(".env"), env_content)
            file_repo.set_permissions(Path(".env"), 0o600)

            assert service.should_update_web_search_settings() is False

    def test_get_master_key(self, project_root: Path):
        """Test getting Master Key from .env."""
        service = ConfigService(project_root)
        file_repo = service.file_repo

        env_content = "LITELLM_MASTER_KEY=sk-master-key-456\n"
        file_repo.write_text(Path(".env"), env_content)
        file_repo.set_permissions(Path(".env"), 0o600)

        master_key = service.get_master_key()
        assert master_key == "sk-master-key-456"

    def test_get_master_key_missing(self, project_root: Path):
        """Test getting Master Key when not set."""
        service = ConfigService(project_root)
        master_key = service.get_master_key()
        assert master_key == ""

















