"""
Unit tests for core.config module
"""

from pathlib import Path

import pytest

from src.core.config import (
    AppConfig,
    BudgetProfile,
    PortConfig,
    ResourceProfile,
)
from src.core.constants import (
    DEFAULT_LITELLM_PORT,
    DEFAULT_POSTGRES_PORT,
    DEFAULT_UI_USERNAME,
    DEFAULT_WEBUI_INTERNAL_PORT,
)


@pytest.mark.unit
class TestResourceProfile:
    """Tests for ResourceProfile enum

    See docs/configuration.md#resource-profiles and docs/system-requirements.md#resource-profiles
    for detailed specifications.
    """

    def test_resource_profile_values(self):
        """Test that ResourceProfile has correct values per documentation"""
        assert ResourceProfile.DESKTOP == "desktop"
        assert ResourceProfile.SMALL_VPS == "small"
        assert ResourceProfile.MEDIUM_VPS == "medium"
        assert ResourceProfile.LARGE_VPS == "large"

    def test_resource_profile_is_enum(self):
        """Test that ResourceProfile is an Enum"""
        assert isinstance(ResourceProfile.DESKTOP, ResourceProfile)
        assert isinstance(ResourceProfile.MEDIUM_VPS, ResourceProfile)

    def test_resource_profile_string_comparison(self):
        """Test that ResourceProfile can be compared with strings"""
        assert ResourceProfile.DESKTOP == "desktop"
        assert ResourceProfile.MEDIUM_VPS == "medium"
        assert ResourceProfile.SMALL_VPS.value == "small"

    def test_resource_profile_all_values(self):
        """Test that all expected ResourceProfile values exist"""
        expected_values = {"desktop", "small", "medium", "large"}
        actual_values = {profile.value for profile in ResourceProfile}
        assert actual_values == expected_values

    def test_resource_profile_matches_documentation(self):
        """
        Test that ResourceProfile enum values match documentation.

        See docs/configuration.md#resource-profiles:
        - Desktop/Local: unlimited resources
        - Small VPS: 2GB RAM, 2 CPU, 1-2 users
        - Medium VPS: 4GB RAM, 4 CPU, 3-5 users (recommended)
        - Large VPS: 8GB+ RAM, 8 CPU, 10+ users
        """
        # Verify enum values match documented names
        assert ResourceProfile.DESKTOP.value == "desktop"
        assert ResourceProfile.SMALL_VPS.value == "small"
        assert ResourceProfile.MEDIUM_VPS.value == "medium"
        assert ResourceProfile.LARGE_VPS.value == "large"

    def test_resource_profile_matches_config_dict(self):
        """
        Test that ResourceProfile enum values match RESOURCE_PROFILES dict.

        This ensures consistency between core/config.py (enum) and src/config.py (dict).
        See src/config.py for RESOURCE_PROFILES dict with RAM, CPU, workers details.
        """
        from src.config import RESOURCE_PROFILES

        # Verify all enum values have corresponding entries in RESOURCE_PROFILES
        for profile in ResourceProfile:
            assert profile in RESOURCE_PROFILES, f"ResourceProfile {profile} not found in RESOURCE_PROFILES"
            info = RESOURCE_PROFILES[profile]
            assert "name" in info
            assert "cpu_cores" in info
            assert "ram" in info
            assert "workers" in info

    def test_resource_profile_matches_docker_compose_templates(self):
        """
        Test that ResourceProfile enum values match PROFILE_TEMPLATES.

        This ensures consistency between core/config.py (enum) and docker_compose.py (templates).
        See src/docker_compose.py for PROFILE_TEMPLATES with num_workers.
        """
        from src.docker_compose import PROFILE_TEMPLATES

        # Verify all enum values have corresponding entries in PROFILE_TEMPLATES
        for profile in ResourceProfile:
            assert profile in PROFILE_TEMPLATES, f"ResourceProfile {profile} not found in PROFILE_TEMPLATES"
            template = PROFILE_TEMPLATES[profile]
            assert "litellm" in template
            assert "num_workers" in template["litellm"]

    def test_resource_profile_workers_match_documentation(self):
        """
        Test that workers count matches documentation.

        See docs/system-requirements.md#resource-profiles:
        - Desktop: 4 workers (unlimited resources)
        - Small VPS: 1 worker (2GB RAM, actual usage ~2.3-2.5GB)
        - Medium VPS: 2 workers (4GB RAM, uses ~3.3GB)
        - Large VPS: 6 workers (8GB+ RAM, uses ~5.1GB)
        """
        from src.docker_compose import PROFILE_TEMPLATES

        expected_workers = {
            ResourceProfile.DESKTOP: 4,
            ResourceProfile.SMALL_VPS: 1,
            ResourceProfile.MEDIUM_VPS: 2,
            ResourceProfile.LARGE_VPS: 6,
        }

        for profile, expected_count in expected_workers.items():
            actual_count = PROFILE_TEMPLATES[profile]["litellm"]["num_workers"]
            assert actual_count == expected_count, (
                f"ResourceProfile {profile} has {actual_count} workers, "
                f"expected {expected_count} per documentation"
            )


@pytest.mark.unit
class TestBudgetProfile:
    """Tests for BudgetProfile enum

    See docs/configuration.md#budget-profiles for budget limits:
    - test: $15/month
    - prod: $200/month
    - unlimited: $1000/month
    """

    def test_budget_profile_values(self):
        """Test that BudgetProfile has correct values per documentation"""
        assert BudgetProfile.TEST == "test"
        assert BudgetProfile.PROD == "prod"
        assert BudgetProfile.UNLIMITED == "unlimited"

    def test_budget_profile_is_enum(self):
        """Test that BudgetProfile is an Enum"""
        assert isinstance(BudgetProfile.TEST, BudgetProfile)
        assert isinstance(BudgetProfile.PROD, BudgetProfile)

    def test_budget_profile_string_comparison(self):
        """Test that BudgetProfile can be compared with strings"""
        assert BudgetProfile.TEST == "test"
        assert BudgetProfile.PROD == "prod"
        assert BudgetProfile.UNLIMITED.value == "unlimited"

    def test_budget_profile_all_values(self):
        """Test that all expected BudgetProfile values exist"""
        expected_values = {"test", "prod", "unlimited"}
        actual_values = {profile.value for profile in BudgetProfile}
        assert actual_values == expected_values

    def test_budget_profile_matches_documentation(self):
        """
        Test that BudgetProfile enum values match documentation.

        See docs/configuration.md#budget-profiles:
        - test: $15/month (Test environment)
        - prod: $200/month (Regular use)
        - unlimited: $1000/month (No limits)
        """
        # Verify enum values match documented names
        assert BudgetProfile.TEST.value == "test"
        assert BudgetProfile.PROD.value == "prod"
        assert BudgetProfile.UNLIMITED.value == "unlimited"

    def test_budget_profile_matches_budgets_dict(self):
        """
        Test that BudgetProfile enum values match BUDGET_PROFILES dict.

        This ensures consistency between core/config.py (enum) and budgets.py (dict).
        See src/budgets.py for BUDGET_PROFILES dict with budget limits.
        """
        from src.budgets import BUDGET_PROFILES

        # Verify all enum values have corresponding entries in BUDGET_PROFILES
        for profile in BudgetProfile:
            assert profile.value in BUDGET_PROFILES, (
                f"BudgetProfile {profile} not found in BUDGET_PROFILES"
            )
            budget_info = BUDGET_PROFILES[profile.value]
            assert "description" in budget_info
            assert "general_budget" in budget_info

    def test_budget_profile_limits_match_documentation(self):
        """
        Test that budget limits match documentation.

        See docs/configuration.md#budget-profiles:
        - test: $15/month
        - prod: $200/month
        - unlimited: $1000/month
        """
        from src.budgets import BUDGET_PROFILES

        expected_budgets = {
            BudgetProfile.TEST: 15.0,
            BudgetProfile.PROD: 200.0,
            BudgetProfile.UNLIMITED: 1000.0,
        }

        for profile, expected_budget in expected_budgets.items():
            actual_budget = BUDGET_PROFILES[profile.value]["general_budget"]
            assert actual_budget == expected_budget, (
                f"BudgetProfile {profile} has ${actual_budget}/month, "
                f"expected ${expected_budget}/month per documentation"
            )


@pytest.mark.unit
class TestPortConfig:
    """Tests for PortConfig dataclass"""

    def test_port_config_defaults(self):
        """Test PortConfig default values"""
        config = PortConfig()
        assert config.postgres_port == DEFAULT_POSTGRES_PORT
        assert config.litellm_internal_port == DEFAULT_LITELLM_PORT
        assert config.webui_internal_port == DEFAULT_WEBUI_INTERNAL_PORT
        assert config.litellm_external_port == DEFAULT_LITELLM_PORT
        assert config.webui_external_port is None
        assert config.use_nginx is False
        assert config.use_ssl is False
        assert config.ssl_domain is None
        assert config.nginx_http_port is None
        assert config.nginx_https_port is None
        assert config.nginx_port is None

    def test_port_config_custom_values(self):
        """Test PortConfig with custom values"""
        config = PortConfig(
            postgres_port=5433,
            litellm_internal_port=4001,
            webui_internal_port=8081,
            litellm_external_port=4001,
            webui_external_port=3001,
            use_nginx=True,
            use_ssl=True,
            ssl_domain="example.com",
            nginx_http_port=80,
            nginx_https_port=443,
            nginx_port=80,
        )
        assert config.postgres_port == 5433
        assert config.litellm_internal_port == 4001
        assert config.webui_internal_port == 8081
        assert config.litellm_external_port == 4001
        assert config.webui_external_port == 3001
        assert config.use_nginx is True
        assert config.use_ssl is True
        assert config.ssl_domain == "example.com"
        assert config.nginx_http_port == 80
        assert config.nginx_https_port == 443
        assert config.nginx_port == 80

    def test_port_config_to_dict(self):
        """Test PortConfig.to_dict() method"""
        config = PortConfig(
            postgres_port=5432,
            litellm_internal_port=4000,
            webui_internal_port=8080,
            litellm_external_port=4000,
            webui_external_port=None,
            use_nginx=True,
            nginx_http_port=63345,
        )
        result = config.to_dict()

        assert isinstance(result, dict)
        assert result["postgres_port"] == 5432
        assert result["litellm_internal_port"] == 4000
        assert result["webui_internal_port"] == 8080
        assert result["litellm_external_port"] == 4000
        assert result["webui_external_port"] is None
        assert result["use_nginx"] is True
        assert result["use_ssl"] is False
        assert result["ssl_domain"] is None
        assert result["nginx_http_port"] == 63345
        assert result["nginx_https_port"] is None
        assert result["nginx_port"] is None

    def test_port_config_from_dict(self):
        """Test PortConfig.from_dict() method"""
        data = {
            "postgres_port": 5432,
            "litellm_internal_port": 4000,
            "webui_internal_port": 8080,
            "litellm_external_port": 4000,
            "webui_external_port": 3000,
            "use_nginx": False,
            "use_ssl": False,
            "ssl_domain": None,
            "nginx_http_port": None,
            "nginx_https_port": None,
            "nginx_port": None,
        }
        config = PortConfig.from_dict(data)

        assert isinstance(config, PortConfig)
        assert config.postgres_port == 5432
        assert config.litellm_internal_port == 4000
        assert config.webui_internal_port == 8080
        assert config.litellm_external_port == 4000
        assert config.webui_external_port == 3000
        assert config.use_nginx is False

    def test_port_config_round_trip(self):
        """Test PortConfig to_dict() and from_dict() round trip"""
        original = PortConfig(
            postgres_port=5432,
            litellm_internal_port=4000,
            webui_internal_port=8080,
            litellm_external_port=4000,
            webui_external_port=3000,
            use_nginx=True,
            use_ssl=True,
            ssl_domain="example.com",
            nginx_http_port=80,
            nginx_https_port=443,
            nginx_port=80,
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = PortConfig.from_dict(data)

        # Check all fields match
        assert restored.postgres_port == original.postgres_port
        assert restored.litellm_internal_port == original.litellm_internal_port
        assert restored.webui_internal_port == original.webui_internal_port
        assert restored.litellm_external_port == original.litellm_external_port
        assert restored.webui_external_port == original.webui_external_port
        assert restored.use_nginx == original.use_nginx
        assert restored.use_ssl == original.use_ssl
        assert restored.ssl_domain == original.ssl_domain
        assert restored.nginx_http_port == original.nginx_http_port
        assert restored.nginx_https_port == original.nginx_https_port
        assert restored.nginx_port == original.nginx_port

    def test_port_config_with_nginx(self):
        """Test PortConfig with nginx enabled"""
        config = PortConfig(
            use_nginx=True,
            nginx_http_port=63345,
            nginx_port=63345,
            litellm_external_port=4000,
            webui_external_port=None,  # Not exposed when nginx is used
        )
        assert config.use_nginx is True
        assert config.nginx_http_port == 63345
        assert config.webui_external_port is None  # Via nginx

    def test_port_config_without_nginx(self):
        """Test PortConfig without nginx"""
        config = PortConfig(
            use_nginx=False,
            litellm_external_port=4000,
            webui_external_port=3000,
        )
        assert config.use_nginx is False
        assert config.litellm_external_port == 4000
        assert config.webui_external_port == 3000
        assert config.nginx_http_port is None


@pytest.mark.unit
class TestAppConfig:
    """Tests for AppConfig dataclass"""

    def test_app_config_required_fields(self, temp_dir: Path):
        """Test AppConfig with required fields only"""
        config = AppConfig(project_root=temp_dir)

        assert config.project_root == temp_dir
        assert config.resource_profile == ResourceProfile.MEDIUM_VPS
        assert config.budget_profile == BudgetProfile.TEST
        assert isinstance(config.port_config, PortConfig)
        assert config.master_key is None
        assert config.ui_username == DEFAULT_UI_USERNAME
        assert config.ui_password is None
        assert config.postgres_password is None
        assert config.webui_secret is None

    def test_app_config_defaults(self, temp_dir: Path):
        """Test AppConfig default values"""
        config = AppConfig(project_root=temp_dir)

        # Check defaults
        assert config.resource_profile == ResourceProfile.MEDIUM_VPS
        assert config.budget_profile == BudgetProfile.TEST
        assert config.ui_username == DEFAULT_UI_USERNAME
        assert isinstance(config.port_config, PortConfig)

    def test_app_config_custom_values(self, temp_dir: Path):
        """Test AppConfig with custom values"""
        port_config = PortConfig(use_nginx=True, nginx_http_port=63345)
        config = AppConfig(
            project_root=temp_dir,
            resource_profile=ResourceProfile.LARGE_VPS,
            budget_profile=BudgetProfile.PROD,
            port_config=port_config,
            master_key="test-key",
            ui_username="custom_user",
            ui_password="test-password",
            postgres_password="postgres-pass",
            webui_secret="webui-secret",
        )

        assert config.project_root == temp_dir
        assert config.resource_profile == ResourceProfile.LARGE_VPS
        assert config.budget_profile == BudgetProfile.PROD
        assert config.port_config == port_config
        assert config.master_key == "test-key"
        assert config.ui_username == "custom_user"
        assert config.ui_password == "test-password"
        assert config.postgres_password == "postgres-pass"
        assert config.webui_secret == "webui-secret"

    def test_app_config_env_file_property(self, temp_dir: Path):
        """Test AppConfig.env_file property"""
        config = AppConfig(project_root=temp_dir)
        env_file = config.env_file

        assert isinstance(env_file, Path)
        assert env_file == temp_dir / ".env"
        assert env_file.parent == temp_dir

    def test_app_config_config_yaml_property(self, temp_dir: Path):
        """Test AppConfig.config_yaml property"""
        config = AppConfig(project_root=temp_dir)
        config_yaml = config.config_yaml

        assert isinstance(config_yaml, Path)
        assert config_yaml == temp_dir / "config.yaml"
        assert config_yaml.parent == temp_dir

    def test_app_config_docker_compose_override_property(self, temp_dir: Path):
        """Test AppConfig.docker_compose_override property"""
        config = AppConfig(project_root=temp_dir)
        docker_compose = config.docker_compose_override

        assert isinstance(docker_compose, Path)
        assert docker_compose == temp_dir / "docker-compose.override.yml"
        assert docker_compose.parent == temp_dir

    def test_app_config_nginx_config_dir_property(self, temp_dir: Path):
        """Test AppConfig.nginx_config_dir property"""
        config = AppConfig(project_root=temp_dir)
        nginx_dir = config.nginx_config_dir

        assert isinstance(nginx_dir, Path)
        assert nginx_dir == temp_dir / "nginx" / "conf.d"
        assert nginx_dir.parent == temp_dir / "nginx"
        assert nginx_dir.parent.parent == temp_dir

    def test_app_config_path_properties_are_paths(self, temp_dir: Path):
        """Test that all path properties return Path objects"""
        config = AppConfig(project_root=temp_dir)

        assert isinstance(config.env_file, Path)
        assert isinstance(config.config_yaml, Path)
        assert isinstance(config.docker_compose_override, Path)
        assert isinstance(config.nginx_config_dir, Path)

    def test_app_config_with_different_resource_profiles(self, temp_dir: Path):
        """Test AppConfig with different resource profiles"""
        for profile in ResourceProfile:
            config = AppConfig(project_root=temp_dir, resource_profile=profile)
            assert config.resource_profile == profile

    def test_app_config_with_different_budget_profiles(self, temp_dir: Path):
        """Test AppConfig with different budget profiles"""
        for profile in BudgetProfile:
            config = AppConfig(project_root=temp_dir, budget_profile=profile)
            assert config.budget_profile == profile

    def test_app_config_port_config_independence(self, temp_dir: Path):
        """Test that PortConfig instances are independent"""
        config1 = AppConfig(project_root=temp_dir)
        config2 = AppConfig(project_root=temp_dir)

        # Modify port config in one
        config1.port_config.use_nginx = True
        config1.port_config.nginx_http_port = 63345

        # Other should be unaffected
        assert config2.port_config.use_nginx is False
        assert config2.port_config.nginx_http_port is None

