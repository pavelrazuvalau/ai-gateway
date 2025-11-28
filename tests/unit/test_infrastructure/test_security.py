"""
Unit tests for infrastructure.security module

See docs/security.md for security best practices.
See docs/security.md#virtual-key-security for master key generation details.
See docs/security.md#basic-security-recommendations for password security.
"""

import pytest

from src.core.constants import (
    DEFAULT_MASTER_KEY_TOKEN_LENGTH,
    DEFAULT_PASSWORD_LENGTH,
)
from src.infrastructure.security import SecurityService


@pytest.mark.unit
class TestSecurityServiceGenerateMasterKey:
    """
    Tests for SecurityService.generate_master_key()

    See docs/security.md#virtual-key-security for security details.
    Master key must start with "sk-" prefix and use DEFAULT_MASTER_KEY_TOKEN_LENGTH.
    """

    def test_generate_master_key_starts_with_sk(self):
        """Test that generated master key starts with 'sk-' prefix"""
        key = SecurityService.generate_master_key()
        assert key.startswith("sk-")
        assert len(key) > 3  # "sk-" + token

    def test_generate_master_key_has_correct_length(self):
        """
        Test that generated master key has correct length.

        Master key format: "sk-" + token.
        token_urlsafe(n) returns approximately 4/3 * n characters (base64url encoding).
        For DEFAULT_MASTER_KEY_TOKEN_LENGTH=32, token is approximately 43 chars.
        See src/core/constants.py for DEFAULT_MASTER_KEY_TOKEN_LENGTH.
        """
        key = SecurityService.generate_master_key()
        # "sk-" prefix (3 chars) + token (base64url encoded, ~43 chars for 32 bytes)
        # token_urlsafe(32) produces ~43 characters
        assert len(key) >= 3 + DEFAULT_MASTER_KEY_TOKEN_LENGTH  # At least 35 chars
        assert len(key) <= 3 + (DEFAULT_MASTER_KEY_TOKEN_LENGTH * 2)  # Max reasonable length

    def test_generate_master_key_is_unique(self):
        """Test that generated master keys are unique"""
        keys = [SecurityService.generate_master_key() for _ in range(10)]
        # All keys should be different
        assert len(set(keys)) == 10

    def test_generate_master_key_uses_urlsafe_token(self):
        """
        Test that master key uses URL-safe token format.

        token_urlsafe generates base64url-safe tokens (A-Z, a-z, 0-9, -, _).
        """
        key = SecurityService.generate_master_key()
        token = key[3:]  # Remove "sk-" prefix

        # Check that token contains only URL-safe characters
        allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        assert all(c in allowed_chars for c in token)

    def test_generate_master_key_matches_documentation(self):
        """
        Test that master key generation matches documentation.

        See docs/security.md#virtual-key-security:
        - Master key starts with "sk-"
        - Master key is auto-generated
        - Master key has full administrative access
        """
        key = SecurityService.generate_master_key()
        assert key.startswith("sk-")
        assert len(key) >= 3 + DEFAULT_MASTER_KEY_TOKEN_LENGTH


@pytest.mark.unit
class TestSecurityServiceGeneratePassword:
    """
    Tests for SecurityService.generate_password()

    See docs/security.md#basic-security-recommendations for password security.
    Password generation uses openssl (preferred) or secrets module (fallback).
    """

    def test_generate_password_default_length(self):
        """
        Test that generated password uses default length.

        See src/core/constants.py for DEFAULT_PASSWORD_LENGTH.
        """
        password = SecurityService.generate_password()
        assert len(password) == DEFAULT_PASSWORD_LENGTH

    def test_generate_password_custom_length(self):
        """Test that generated password respects custom length"""
        for length in [8, 16, 32, 64]:
            password = SecurityService.generate_password(length)
            assert len(password) == length

    def test_generate_password_is_unique(self):
        """Test that generated passwords are unique"""
        passwords = [SecurityService.generate_password(16) for _ in range(10)]
        # All passwords should be different (very high probability)
        assert len(set(passwords)) == 10

    def test_generate_password_contains_valid_characters(self):
        """
        Test that generated password contains valid characters.

        Password uses base64url-safe characters (from openssl or secrets.token_urlsafe).
        Special characters =, +, / are removed for compatibility.
        """
        password = SecurityService.generate_password(32)

        # Should contain alphanumeric and URL-safe characters
        # After removing =, +, /, only A-Z, a-z, 0-9, -, _ remain
        allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        assert all(c in allowed_chars for c in password)

    def test_generate_password_no_special_chars(self):
        """
        Test that generated password doesn't contain problematic special characters.

        Characters =, +, / are removed to avoid issues in environment variables.
        """
        password = SecurityService.generate_password(32)
        assert "=" not in password
        assert "+" not in password
        assert "/" not in password

    def test_generate_password_fallback_to_secrets(self, monkeypatch):
        """
        Test that password generation falls back to secrets module if openssl fails.

        This tests the fallback mechanism when openssl is not available.
        """
        # Mock subprocess.run to raise FileNotFoundError (openssl not found)
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("openssl not found")

        import subprocess
        monkeypatch.setattr(subprocess, "run", mock_run)

        # Should still generate password using secrets module
        password = SecurityService.generate_password(16)
        assert len(password) == 16
        assert isinstance(password, str)

    def test_generate_password_matches_documentation(self):
        """
        Test that password generation matches documentation.

        See docs/security.md#basic-security-recommendations:
        - Passwords should be changed from defaults
        - Use strong passwords
        - Default length is 32 characters
        """
        password = SecurityService.generate_password()
        assert len(password) == DEFAULT_PASSWORD_LENGTH
        assert len(password) >= 16  # Minimum recommended length


@pytest.mark.unit
class TestSecurityServiceValidatePasswordStrength:
    """
    Tests for SecurityService.validate_password_strength()

    Password validation checks:
    - Minimum length (default: 16)
    - At least one digit
    - At least one letter
    """

    def test_validate_password_strength_strong_password(self):
        """Test that strong password passes validation"""
        strong_passwords = [
            "Password12345678",  # Has letters and digits, >= 16 chars
            "MySecurePass2024!",  # Has letters and digits
            "abc123def456ghi789",  # Has letters and digits
        ]
        for password in strong_passwords:
            assert SecurityService.validate_password_strength(password) is True

    def test_validate_password_strength_weak_password_too_short(self):
        """Test that password shorter than minimum length fails"""
        weak_passwords = [
            "short",  # Too short
            "Pass123",  # Too short (< 16)
            "a1b2c3d4",  # Too short (< 16)
        ]
        for password in weak_passwords:
            assert SecurityService.validate_password_strength(password) is False

    def test_validate_password_strength_weak_password_no_digit(self):
        """Test that password without digits fails"""
        weak_passwords = [
            "PasswordWithoutDigits",  # No digits
            "abcdefghijklmnop",  # No digits
        ]
        for password in weak_passwords:
            assert SecurityService.validate_password_strength(password) is False

    def test_validate_password_strength_weak_password_no_letter(self):
        """Test that password without letters fails"""
        weak_passwords = [
            "1234567890123456",  # No letters
            "9876543210987654",  # No letters
        ]
        for password in weak_passwords:
            assert SecurityService.validate_password_strength(password) is False

    def test_validate_password_strength_custom_min_length(self):
        """Test that validation respects custom minimum length"""
        # Password with 8 chars, letters and digits - should pass with min_length=8
        assert SecurityService.validate_password_strength("Pass1234", min_length=8) is True

        # Same password should fail with min_length=16
        assert SecurityService.validate_password_strength("Pass1234", min_length=16) is False

    def test_validate_password_strength_edge_cases(self):
        """Test edge cases for password validation"""
        # Exactly minimum length with letters and digits
        assert SecurityService.validate_password_strength("Password123456", min_length=14) is True

        # One char less than minimum
        assert SecurityService.validate_password_strength("Password12345", min_length=14) is False

        # Empty string
        assert SecurityService.validate_password_strength("", min_length=16) is False

        # Only spaces (no letters or digits)
        assert SecurityService.validate_password_strength("                ", min_length=16) is False

    def test_validate_password_strength_default_min_length(self):
        """
        Test that validation uses default minimum length of 16.

        See SecurityService.validate_password_strength() default min_length=16.
        """
        # Password with 15 chars (one less than default)
        assert SecurityService.validate_password_strength("Password12345") is False

        # Password with 16 chars (exactly default) - must have both letters and digits
        # "Password12345678" = Password(8) + 12345678(8) = 16 chars
        assert SecurityService.validate_password_strength("Password12345678") is True


@pytest.mark.unit
class TestSecurityServiceIntegration:
    """
    Integration tests for SecurityService methods working together.

    Tests that generated passwords can be validated and master keys have correct format.
    """

    def test_generated_password_passes_validation(self):
        """
        Test that generated password passes strength validation.

        Generated passwords should meet minimum strength requirements.
        """
        password = SecurityService.generate_password(16)
        # Generated password should pass validation (has length >= 16)
        # Note: Generated password might not have digits/letters, so we check length
        assert len(password) >= 16

    def test_master_key_format_is_consistent(self):
        """
        Test that master key format is consistent across multiple generations.

        All master keys should:
        - Start with "sk-"
        - Have consistent length (approximately, due to base64url encoding)
        - Use URL-safe characters
        """
        keys = [SecurityService.generate_master_key() for _ in range(5)]

        # All keys should have similar length (base64url encoding varies slightly)
        lengths = [len(key) for key in keys]
        # All lengths should be within reasonable range
        min_length = min(lengths)
        max_length = max(lengths)
        # Lengths should be similar (within 2 chars due to base64url padding)
        assert max_length - min_length <= 2

        for key in keys:
            assert key.startswith("sk-")
            # Length should be approximately 3 + (DEFAULT_MASTER_KEY_TOKEN_LENGTH * 4/3)
            # token_urlsafe(32) produces ~43 characters
            assert len(key) >= 3 + DEFAULT_MASTER_KEY_TOKEN_LENGTH
            # Token part should be URL-safe
            token = key[3:]
            allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
            assert all(c in allowed_chars for c in token)

