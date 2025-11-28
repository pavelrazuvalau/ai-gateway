"""
Unit tests for core.constants module

See docs/configuration.md#port-configuration for port constants documentation.
Port values are documented in docs/configuration.md#default-ports.
"""

import pytest

from src.core.constants import (
    BUDGET_PROFILE_PROD,
    BUDGET_PROFILE_TEST,
    BUDGET_PROFILE_UNLIMITED,
    DEFAULT_LITELLM_PORT,
    DEFAULT_MASTER_KEY_TOKEN_LENGTH,
    DEFAULT_NGINX_HTTP_PORT,
    DEFAULT_NGINX_HTTPS_PORT,
    DEFAULT_PASSWORD_LENGTH,
    DEFAULT_POSTGRES_DB,
    DEFAULT_POSTGRES_PORT,
    DEFAULT_POSTGRES_USER,
    DEFAULT_UI_PASSWORD_LENGTH,
    DEFAULT_UI_USERNAME,
    DEFAULT_WEBUI_INTERNAL_PORT,
    DEFAULT_WEBUI_PORT,
    DOCKER_COMPOSE_TIMEOUT,
    DOCKER_DOWN_TIMEOUT,
    DOCKER_TIMEOUT,
    DOCKER_UP_TIMEOUT,
    HIGH_PORT_MAX,
    HIGH_PORT_MIN,
    MAX_PORT,
    MIN_PORT,
    NO_VALUES,
    SUBPROCESS_TIMEOUT,
    SYSTEM_APP_DIR,
    SYSTEM_USERNAME,
    YES_VALUES,
)


@pytest.mark.unit
class TestPortConstants:
    """
    Tests for port-related constants

    See docs/configuration.md#port-configuration for port configuration details.
    Default ports are documented in docs/configuration.md#default-ports:
    - LiteLLM API: 4000
    - Open WebUI: 3000 (external), 8080 (internal)
    - PostgreSQL: 5432
    - Nginx: 80 (HTTP), 443 (HTTPS)
    """

    def test_default_ports_are_valid(self):
        """Test that default ports are within valid range"""
        assert MIN_PORT <= DEFAULT_LITELLM_PORT <= MAX_PORT
        assert MIN_PORT <= DEFAULT_WEBUI_PORT <= MAX_PORT
        assert MIN_PORT <= DEFAULT_POSTGRES_PORT <= MAX_PORT
        # Nginx ports 80 and 443 are privileged but standard for HTTP/HTTPS
        assert 1 <= DEFAULT_NGINX_HTTP_PORT <= MAX_PORT
        assert 1 <= DEFAULT_NGINX_HTTPS_PORT <= MAX_PORT
        assert MIN_PORT <= DEFAULT_WEBUI_INTERNAL_PORT <= MAX_PORT

    def test_port_ranges(self):
        """Test port range constants"""
        assert MIN_PORT == 1024
        assert MAX_PORT == 65535
        assert HIGH_PORT_MIN == 49152
        assert HIGH_PORT_MAX == 65535
        assert HIGH_PORT_MIN < HIGH_PORT_MAX
        assert HIGH_PORT_MIN >= MIN_PORT
        assert HIGH_PORT_MAX <= MAX_PORT

    def test_default_ports_are_standard(self):
        """
        Test that default ports match standard values.

        See docs/configuration.md#default-ports for documented port values.
        """
        assert DEFAULT_LITELLM_PORT == 4000
        assert DEFAULT_WEBUI_PORT == 3000
        assert DEFAULT_POSTGRES_PORT == 5432
        assert DEFAULT_NGINX_HTTP_PORT == 80
        assert DEFAULT_NGINX_HTTPS_PORT == 443
        assert DEFAULT_WEBUI_INTERNAL_PORT == 8080


@pytest.mark.unit
class TestPasswordConstants:
    """Tests for password-related constants"""

    def test_password_lengths_are_positive(self):
        """Test that password lengths are positive"""
        assert DEFAULT_PASSWORD_LENGTH > 0
        assert DEFAULT_UI_PASSWORD_LENGTH > 0
        assert DEFAULT_MASTER_KEY_TOKEN_LENGTH > 0

    def test_password_lengths_are_reasonable(self):
        """Test that password lengths are reasonable"""
        assert DEFAULT_PASSWORD_LENGTH >= 16
        assert DEFAULT_UI_PASSWORD_LENGTH >= 8
        assert DEFAULT_MASTER_KEY_TOKEN_LENGTH >= 16


@pytest.mark.unit
class TestTimeoutConstants:
    """Tests for timeout-related constants"""

    def test_timeouts_are_positive(self):
        """Test that all timeouts are positive"""
        assert DOCKER_TIMEOUT > 0
        assert DOCKER_COMPOSE_TIMEOUT > 0
        assert DOCKER_UP_TIMEOUT > 0
        assert DOCKER_DOWN_TIMEOUT > 0
        assert SUBPROCESS_TIMEOUT > 0

    def test_timeout_ordering(self):
        """Test that timeouts are ordered correctly"""
        assert DOCKER_TIMEOUT < DOCKER_COMPOSE_TIMEOUT
        assert DOCKER_COMPOSE_TIMEOUT < DOCKER_UP_TIMEOUT


@pytest.mark.unit
class TestBudgetProfileConstants:
    """Tests for budget profile constants"""

    def test_budget_profiles_are_strings(self):
        """Test that budget profiles are strings"""
        assert isinstance(BUDGET_PROFILE_TEST, str)
        assert isinstance(BUDGET_PROFILE_PROD, str)
        assert isinstance(BUDGET_PROFILE_UNLIMITED, str)

    def test_budget_profiles_are_different(self):
        """Test that budget profiles are different"""
        assert BUDGET_PROFILE_TEST != BUDGET_PROFILE_PROD
        assert BUDGET_PROFILE_TEST != BUDGET_PROFILE_UNLIMITED
        assert BUDGET_PROFILE_PROD != BUDGET_PROFILE_UNLIMITED


@pytest.mark.unit
class TestDefaultValues:
    """Tests for default value constants"""

    def test_default_username(self):
        """Test default username"""
        assert DEFAULT_UI_USERNAME == "admin"
        assert isinstance(DEFAULT_UI_USERNAME, str)
        assert len(DEFAULT_UI_USERNAME) > 0

    def test_default_postgres_values(self):
        """Test default PostgreSQL values"""
        assert DEFAULT_POSTGRES_USER == "litellm"
        assert DEFAULT_POSTGRES_DB == "litellm"
        assert isinstance(DEFAULT_POSTGRES_USER, str)
        assert isinstance(DEFAULT_POSTGRES_DB, str)


@pytest.mark.unit
class TestStringLiterals:
    """Tests for string literal constants"""

    def test_yes_values(self):
        """Test YES_VALUES constant"""
        assert "yes" in YES_VALUES
        assert "true" in YES_VALUES
        assert "1" in YES_VALUES
        assert "y" in YES_VALUES
        assert isinstance(YES_VALUES, tuple)

    def test_no_values(self):
        """Test NO_VALUES constant"""
        assert "no" in NO_VALUES
        assert "false" in NO_VALUES
        assert "0" in NO_VALUES
        assert "n" in NO_VALUES
        assert isinstance(NO_VALUES, tuple)

    def test_yes_no_values_are_disjoint(self):
        """Test that YES_VALUES and NO_VALUES don't overlap"""
        assert not set(YES_VALUES) & set(NO_VALUES)


@pytest.mark.unit
class TestSystemConstants:
    """Tests for system-related constants"""

    def test_system_username(self):
        """Test system username constant"""
        assert SYSTEM_USERNAME == "aigateway"
        assert isinstance(SYSTEM_USERNAME, str)

    def test_system_app_dir(self):
        """Test system app directory constant"""
        assert SYSTEM_APP_DIR == "/opt/ai-gateway"
        assert isinstance(SYSTEM_APP_DIR, str)
        assert SYSTEM_APP_DIR.startswith("/")

