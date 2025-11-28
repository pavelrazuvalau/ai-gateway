"""
Centralized configuration management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from .constants import (
    DEFAULT_LITELLM_PORT,
    DEFAULT_POSTGRES_PORT,
    DEFAULT_UI_USERNAME,
    DEFAULT_WEBUI_INTERNAL_PORT,
)


class ResourceProfile(str, Enum):
    """
    Resource profile types for system configuration.

    See docs/configuration.md#resource-profiles and docs/system-requirements.md#resource-profiles
    for detailed information about each profile.
    """

    DESKTOP = "desktop"
    SMALL_VPS = "small"
    MEDIUM_VPS = "medium"
    LARGE_VPS = "large"


class BudgetProfile(str, Enum):
    """
    Budget profile types for spending limits.

    See docs/configuration.md#budget-profiles for detailed information.
    """

    TEST = "test"
    PROD = "prod"
    UNLIMITED = "unlimited"


@dataclass
class PortConfig:
    """
    Port configuration for services.

    See docs/configuration.md#port-configuration for detailed information.
    """

    postgres_port: int = DEFAULT_POSTGRES_PORT
    litellm_internal_port: int = DEFAULT_LITELLM_PORT
    webui_internal_port: int = DEFAULT_WEBUI_INTERNAL_PORT
    litellm_external_port: Optional[int] = DEFAULT_LITELLM_PORT
    webui_external_port: Optional[int] = None
    use_nginx: bool = False
    use_ssl: bool = False
    ssl_domain: Optional[str] = None
    nginx_http_port: Optional[int] = None
    nginx_https_port: Optional[int] = None
    nginx_port: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert port configuration to dictionary.

        Returns:
            Dictionary with all port configuration values
        """
        return {
            "postgres_port": self.postgres_port,
            "litellm_internal_port": self.litellm_internal_port,
            "webui_internal_port": self.webui_internal_port,
            "litellm_external_port": self.litellm_external_port,
            "webui_external_port": self.webui_external_port,
            "use_nginx": self.use_nginx,
            "use_ssl": self.use_ssl,
            "ssl_domain": self.ssl_domain,
            "nginx_http_port": self.nginx_http_port,
            "nginx_https_port": self.nginx_https_port,
            "nginx_port": self.nginx_port,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PortConfig:
        """
        Create PortConfig from dictionary.

        Args:
            data: Dictionary with port configuration values

        Returns:
            PortConfig instance
        """
        return cls(**data)


@dataclass
class AppConfig:
    """
    Application configuration dataclass.

    See docs/configuration.md for detailed configuration information.
    """

    project_root: Path
    resource_profile: ResourceProfile = ResourceProfile.MEDIUM_VPS
    budget_profile: BudgetProfile = BudgetProfile.TEST
    port_config: PortConfig = field(default_factory=PortConfig)

    # Security
    master_key: Optional[str] = None
    ui_username: str = DEFAULT_UI_USERNAME
    ui_password: Optional[str] = None
    postgres_password: Optional[str] = None
    webui_secret: Optional[str] = None

    # Paths
    @property
    def env_file(self) -> Path:
        """Path to .env file"""
        return self.project_root / ".env"

    @property
    def config_yaml(self) -> Path:
        """Path to config.yaml"""
        return self.project_root / "config.yaml"

    @property
    def docker_compose_override(self) -> Path:
        """Path to docker-compose.override.yml"""
        return self.project_root / "docker-compose.override.yml"

    @property
    def nginx_config_dir(self) -> Path:
        """Path to nginx config directory"""
        return self.project_root / "nginx" / "conf.d"
