"""
Input validation utilities
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse
from .utils import print_error, print_warning


def validate_port(port: int, min_port: int = 1024, max_port: int = 65535) -> bool:
    """Validate port number"""
    return min_port <= port <= max_port


def validate_url(url: str, require_scheme: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format
    Returns: (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"
    
    url = url.strip()
    
    # Basic format check
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {e}"
    
    if require_scheme and not parsed.scheme:
        return False, "URL must contain scheme (http:// or https://)"
    
    if parsed.scheme not in ('http', 'https'):
        return False, "URL must use http:// or https://"
    
    if not parsed.netloc:
        return False, "URL must contain address (hostname or IP)"
    
    # Check for common issues
    if ' ' in url:
        return False, "URL must not contain spaces"
    
    return True, None


def sanitize_env_value(value: str) -> str:
    """
    Sanitize value for .env file
    Removes dangerous characters that could break .env parsing
    """
    if not value:
        return ""
    
    # Remove newlines and carriage returns
    value = value.replace('\n', '').replace('\r', '')
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Escape quotes if needed (but keep them if they're part of the value)
    # For .env files, we don't need to escape quotes if we're not using them
    
    return value.strip()


def validate_api_key_format(key: str, key_type: str = "generic") -> Tuple[bool, Optional[str]]:
    """
    Validate API key format (basic checks)
    Returns: (is_valid, error_message)
    """
    if not key or not key.strip():
        return False, "API key cannot be empty"
    
    key = key.strip()
    
    # Minimum length check
    if len(key) < 10:
        return False, "API key is too short (minimum 10 characters)"
    
    # Check for common patterns
    if key_type == "anthropic" and not key.startswith("sk-ant-"):
        print_warning("Anthropic API key usually starts with 'sk-ant-'")
    
    if key_type == "openai" and not key.startswith("sk-"):
        print_warning("OpenAI API key usually starts with 'sk-'")
    
    # Check for dangerous characters
    if '\n' in key or '\r' in key:
        return False, "API key must not contain line breaks"
    
    if '\x00' in key:
        return False, "API key contains invalid characters"
    
    return True, None


def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
    """
    Validate domain name format
    Returns: (is_valid, error_message)
    """
    if not domain or not domain.strip():
        return False, "Domain cannot be empty"
    
    domain = domain.strip().lower()
    
    # Basic domain regex
    domain_pattern = re.compile(
        r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$'
    )
    
    if not domain_pattern.match(domain):
        return False, "Invalid domain format"
    
    if len(domain) > 253:
        return False, "Domain is too long (maximum 253 characters)"
    
    return True, None

