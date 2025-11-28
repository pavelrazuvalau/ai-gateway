"""
Unit tests for core.exceptions module

See docs/architecture.md#error-handling for error handling examples.
Custom exceptions are used throughout the codebase for better error context.
"""

import pytest

from src.core.exceptions import (
    AIGatewayError,
    ConfigurationError,
    DockerError,
    FileOperationError,
    PortError,
    SecurityError,
    ValidationError,
)


@pytest.mark.unit
class TestAIGatewayError:
    """
    Tests for AIGatewayError base exception

    See docs/architecture.md#error-handling for error handling patterns.
    All custom exceptions inherit from AIGatewayError for consistent error handling.
    """

    def test_base_exception_creation(self):
        """Test that base exception can be created"""
        error = AIGatewayError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_base_exception_inheritance(self):
        """Test that all custom exceptions inherit from AIGatewayError"""
        assert issubclass(ConfigurationError, AIGatewayError)
        assert issubclass(ValidationError, AIGatewayError)
        assert issubclass(FileOperationError, AIGatewayError)
        assert issubclass(DockerError, AIGatewayError)
        assert issubclass(PortError, AIGatewayError)
        assert issubclass(SecurityError, AIGatewayError)


@pytest.mark.unit
class TestConfigurationError:
    """Tests for ConfigurationError"""

    def test_configuration_error_creation(self):
        """Test that ConfigurationError can be created"""
        error = ConfigurationError("Configuration error")
        assert str(error) == "Configuration error"
        assert isinstance(error, AIGatewayError)
        assert isinstance(error, Exception)

    def test_configuration_error_with_context(self):
        """Test ConfigurationError with context"""
        error = ConfigurationError("Missing required setting: API_KEY")
        assert "API_KEY" in str(error)


@pytest.mark.unit
class TestValidationError:
    """Tests for ValidationError"""

    def test_validation_error_creation(self):
        """Test that ValidationError can be created"""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, AIGatewayError)

    def test_validation_error_for_invalid_port(self):
        """Test ValidationError for invalid port"""
        error = ValidationError("Port must be between 1024 and 65535")
        assert "Port" in str(error)


@pytest.mark.unit
class TestFileOperationError:
    """Tests for FileOperationError"""

    def test_file_operation_error_creation(self):
        """Test that FileOperationError can be created"""
        error = FileOperationError("File not found")
        assert str(error) == "File not found"
        assert isinstance(error, AIGatewayError)

    def test_file_operation_error_for_missing_file(self):
        """Test FileOperationError for missing file"""
        error = FileOperationError("File not found: /path/to/file")
        assert "File not found" in str(error)


@pytest.mark.unit
class TestDockerError:
    """Tests for DockerError"""

    def test_docker_error_creation(self):
        """Test that DockerError can be created"""
        error = DockerError("Docker daemon not running")
        assert str(error) == "Docker daemon not running"
        assert isinstance(error, AIGatewayError)

    def test_docker_error_for_container_failure(self):
        """Test DockerError for container failure"""
        error = DockerError("Failed to start container: litellm")
        assert "container" in str(error).lower()


@pytest.mark.unit
class TestPortError:
    """Tests for PortError"""

    def test_port_error_creation(self):
        """Test that PortError can be created"""
        error = PortError("Port already in use")
        assert str(error) == "Port already in use"
        assert isinstance(error, AIGatewayError)

    def test_port_error_for_conflict(self):
        """Test PortError for port conflict"""
        error = PortError("Port 4000 is already in use by service X")
        assert "4000" in str(error)


@pytest.mark.unit
class TestSecurityError:
    """Tests for SecurityError"""

    def test_security_error_creation(self):
        """Test that SecurityError can be created"""
        error = SecurityError("Security violation")
        assert str(error) == "Security violation"
        assert isinstance(error, AIGatewayError)

    def test_security_error_for_invalid_key(self):
        """Test SecurityError for invalid key"""
        error = SecurityError("Invalid API key format")
        assert "key" in str(error).lower()


@pytest.mark.unit
class TestExceptionChaining:
    """Tests for exception chaining"""

    def test_exception_chaining_with_from(self):
        """Test that exceptions can be chained using 'from'"""
        original_error = ValueError("Original error")
        try:
            raise original_error
        except ValueError:
            # Test that we can create exception with 'from' clause
            # This is a syntax check - actual chaining is tested in integration tests
            try:
                raise ConfigurationError("Configuration failed") from original_error
            except ConfigurationError as wrapped_error:
                assert isinstance(wrapped_error, ConfigurationError)
                assert wrapped_error.__cause__ == original_error

