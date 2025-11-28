"""
Custom exceptions for the application
"""


class AIGatewayError(Exception):
    """Base exception for all application errors"""

    pass


class ConfigurationError(AIGatewayError):
    """Configuration-related errors"""

    pass


class ValidationError(AIGatewayError):
    """Validation errors"""

    pass


class FileOperationError(AIGatewayError):
    """File operation errors"""

    pass


class DockerError(AIGatewayError):
    """Docker-related errors"""

    pass


class PortError(AIGatewayError):
    """Port-related errors"""

    pass


class SecurityError(AIGatewayError):
    """Security-related errors"""

    pass
