"""
Application constants
"""

# Default ports
DEFAULT_LITELLM_PORT = 4000
DEFAULT_WEBUI_PORT = 3000
DEFAULT_POSTGRES_PORT = 5432
DEFAULT_NGINX_HTTP_PORT = 80
DEFAULT_NGINX_HTTPS_PORT = 443
DEFAULT_WEBUI_INTERNAL_PORT = 8080

# Password lengths
DEFAULT_PASSWORD_LENGTH = 32
DEFAULT_UI_PASSWORD_LENGTH = 16
DEFAULT_MASTER_KEY_TOKEN_LENGTH = 32

# Timeouts (in seconds)
DOCKER_TIMEOUT = 5
DOCKER_COMPOSE_TIMEOUT = 30
DOCKER_UP_TIMEOUT = 360  # 6 minutes (increased for --wait with healthchecks)
DOCKER_DOWN_TIMEOUT = 30
SUBPROCESS_TIMEOUT = 5

# Port ranges
MIN_PORT = 1024
MAX_PORT = 65535

# High port range for security (IANA Dynamic/Private Ports)
# Using high ports makes services harder to discover
HIGH_PORT_MIN = 49152  # IANA Dynamic/Private Ports start
HIGH_PORT_MAX = 65535  # Maximum port number

# File permissions
DEFAULT_ENV_FILE_PERMISSIONS = 0o600
DEFAULT_CONFIG_FILE_PERMISSIONS = 0o644

# Budget profiles
BUDGET_PROFILE_TEST = "test"
BUDGET_PROFILE_PROD = "prod"
BUDGET_PROFILE_UNLIMITED = "unlimited"

# Default values
DEFAULT_UI_USERNAME = "admin"
DEFAULT_POSTGRES_USER = "litellm"
DEFAULT_POSTGRES_DB = "litellm"

# String literals
YES_VALUES = ("yes", "true", "1", "y")
NO_VALUES = ("no", "false", "0", "n")

# System user configuration
SYSTEM_USERNAME = "aigateway"
SYSTEM_APP_DIR = "/opt/ai-gateway"

