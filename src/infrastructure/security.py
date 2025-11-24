"""
Security utilities - password generation, key generation
"""

import secrets
import subprocess
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    import logging
from ..core.constants import (
    DEFAULT_PASSWORD_LENGTH, DEFAULT_MASTER_KEY_TOKEN_LENGTH,
    SUBPROCESS_TIMEOUT
)

# Lazy import to avoid circular dependency
def _get_logger() -> 'logging.Logger':
    from .logger import get_logger
    import logging
    return get_logger(__name__)

logger: Optional['logging.Logger'] = None
def get_logger_instance() -> 'logging.Logger':
    import logging
    global logger
    if logger is None:
        logger = _get_logger()
    return logger


class SecurityService:
    """Service for security operations"""
    
    @staticmethod
    def generate_master_key() -> str:
        """
        Generate LiteLLM master key
        
        Returns:
            Master key string (starts with sk-)
        """
        token = secrets.token_urlsafe(DEFAULT_MASTER_KEY_TOKEN_LENGTH)
        key = f"sk-{token}"
        get_logger_instance().debug("Generated master key")
        return key
    
    @staticmethod
    def generate_password(length: int = DEFAULT_PASSWORD_LENGTH) -> str:
        """
        Generate secure random password
        
        Args:
            length: Password length
        
        Returns:
            Generated password
        """
        try:
            # Try using openssl for better randomness
            result = subprocess.run(
                ["openssl", "rand", "-base64", str(length)],
                capture_output=True,
                text=True,
                check=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            password = result.stdout.strip()
            # Remove special characters that might cause issues
            password = password.replace("=", "").replace("+", "").replace("/", "")
            password = password[:length]
            get_logger_instance().debug("Generated password using openssl")
            return password
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback to secrets module
            password = secrets.token_urlsafe(length)[:length]
            get_logger_instance().debug("Generated password using secrets module")
            return password
    
    @staticmethod
    def validate_password_strength(password: str, min_length: int = 16) -> bool:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            min_length: Minimum length
        
        Returns:
            True if password is strong enough
        """
        if len(password) < min_length:
            return False
        
        # Check for at least one digit, one letter
        has_digit = any(c.isdigit() for c in password)
        has_letter = any(c.isalpha() for c in password)
        
        return has_digit and has_letter

