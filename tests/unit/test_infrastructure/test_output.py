"""
Unit tests for infrastructure.output module

This module provides formatted output functions that replace the deprecated
utils.print_* functions. Uses infrastructure.logger under the hood while
maintaining compatibility with the existing API (emojis, colors).

See docs/architecture.md for architecture details.
"""

import os
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.output import (
    Colors,
    ask_yes_no,
    is_non_interactive,
    print_access_urls,
    print_api_info,
    print_error,
    print_header,
    print_info,
    print_status_commands,
    print_step,
    print_success,
    print_warning,
)


@pytest.mark.unit
class TestColors:
    """Tests for Colors class

    See docs/architecture.md for architecture details.
    """

    def test_colors_are_defined(self):
        """Test that all color constants are defined"""
        assert hasattr(Colors, "RED")
        assert hasattr(Colors, "GREEN")
        assert hasattr(Colors, "YELLOW")
        assert hasattr(Colors, "BLUE")
        assert hasattr(Colors, "CYAN")
        assert hasattr(Colors, "RESET")

    def test_colors_are_strings(self):
        """Test that all color constants are strings"""
        assert isinstance(Colors.RED, str)
        assert isinstance(Colors.GREEN, str)
        assert isinstance(Colors.YELLOW, str)
        assert isinstance(Colors.BLUE, str)
        assert isinstance(Colors.CYAN, str)
        assert isinstance(Colors.RESET, str)


@pytest.mark.unit
class TestPrintFunctions:
    """Tests for print_* functions

    See docs/architecture.md for architecture details.
    """

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_error_with_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_error() with TTY (colors enabled)"""
        with patch("sys.stdout.isatty", return_value=True):
            print_error("Test error")
            output = mock_stdout.getvalue()
            assert "❌ Test error" in output
            mock_logger.error.assert_called_once_with("Test error")

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_error_without_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_error() without TTY (no colors)"""
        with patch("sys.stdout.isatty", return_value=False):
            print_error("Test error")
            output = mock_stdout.getvalue()
            assert "❌ Test error" in output
            assert Colors.RED not in output  # No colors when not TTY
            mock_logger.error.assert_called_once_with("Test error")

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_success_with_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_success() with TTY (colors enabled)"""
        with patch("sys.stdout.isatty", return_value=True):
            print_success("Test success")
            output = mock_stdout.getvalue()
            assert "✅ Test success" in output
            mock_logger.info.assert_called_once_with("Test success")

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_warning_with_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_warning() with TTY (colors enabled)"""
        with patch("sys.stdout.isatty", return_value=True):
            print_warning("Test warning")
            output = mock_stdout.getvalue()
            assert "⚠️  Test warning" in output
            mock_logger.warning.assert_called_once_with("Test warning")

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_info_with_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_info() with TTY (colors enabled)"""
        with patch("sys.stdout.isatty", return_value=True):
            print_info("Test info")
            output = mock_stdout.getvalue()
            assert "ℹ️  Test info" in output
            mock_logger.info.assert_called_once_with("Test info")

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_step_with_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_step() with TTY (colors enabled)"""
        with patch("sys.stdout.isatty", return_value=True):
            print_step("Test step")
            output = mock_stdout.getvalue()
            assert "📋 Test step" in output
            mock_logger.info.assert_called_once_with("Test step")

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_header_with_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_header() with TTY (banner with colors)"""
        with patch("sys.stdout.isatty", return_value=True):
            print_header("Test Header")
            output = mock_stdout.getvalue()
            assert "Test Header" in output
            assert "╔" in output  # Banner characters
            assert "╚" in output
            mock_logger.info.assert_called_once_with("=== Test Header ===")

    @patch("src.infrastructure.output.logger")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_header_without_tty(self, mock_stdout: StringIO, mock_logger: MagicMock):
        """Test print_header() without TTY (simple banner)"""
        with patch("sys.stdout.isatty", return_value=False):
            print_header("Test Header")
            output = mock_stdout.getvalue()
            assert "Test Header" in output
            assert "=" in output  # Simple equals signs
            assert "╔" not in output  # No fancy characters
            mock_logger.info.assert_called_once_with("=== Test Header ===")


@pytest.mark.unit
class TestIsNonInteractive:
    """Tests for is_non_interactive() function

    See docs/architecture.md for architecture details.
    """

    def test_is_non_interactive_false_by_default(self, clean_env):
        """Test that is_non_interactive() returns False by default"""
        assert is_non_interactive() is False

    def test_is_non_interactive_true_when_set(self, clean_env):
        """Test that is_non_interactive() returns True when NON_INTERACTIVE=1"""
        os.environ["NON_INTERACTIVE"] = "1"
        assert is_non_interactive() is True

    def test_is_non_interactive_false_when_set_to_0(self, clean_env):
        """Test that is_non_interactive() returns False when NON_INTERACTIVE=0"""
        os.environ["NON_INTERACTIVE"] = "0"
        assert is_non_interactive() is False

    def test_is_non_interactive_false_when_set_to_other(self, clean_env):
        """Test that is_non_interactive() returns False for other values"""
        os.environ["NON_INTERACTIVE"] = "yes"
        assert is_non_interactive() is False


@pytest.mark.unit
class TestAskYesNo:
    """Tests for ask_yes_no() function

    See docs/architecture.md for architecture details.
    """

    @patch("builtins.input", return_value="y")
    def test_ask_yes_no_yes(self, mock_input: MagicMock):
        """Test ask_yes_no() with 'y' input"""
        result = ask_yes_no("Test question?", default=False, non_interactive=False)
        assert result is True
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="n")
    def test_ask_yes_no_no(self, mock_input: MagicMock):
        """Test ask_yes_no() with 'n' input"""
        result = ask_yes_no("Test question?", default=True, non_interactive=False)
        assert result is False
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="")
    def test_ask_yes_no_default_yes(self, mock_input: MagicMock):
        """Test ask_yes_no() with empty input and default=True"""
        result = ask_yes_no("Test question?", default=True, non_interactive=False)
        assert result is True
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="")
    def test_ask_yes_no_default_no(self, mock_input: MagicMock):
        """Test ask_yes_no() with empty input and default=False"""
        result = ask_yes_no("Test question?", default=False, non_interactive=False)
        assert result is False
        mock_input.assert_called_once()

    def test_ask_yes_no_non_interactive_returns_default(self):
        """Test ask_yes_no() in non-interactive mode returns default"""
        result = ask_yes_no("Test question?", default=True, non_interactive=True)
        assert result is True

        result = ask_yes_no("Test question?", default=False, non_interactive=True)
        assert result is False

    def test_ask_yes_no_non_interactive_from_env(self, clean_env):
        """Test ask_yes_no() uses NON_INTERACTIVE env var when non_interactive=None"""
        os.environ["NON_INTERACTIVE"] = "1"
        result = ask_yes_no("Test question?", default=True, non_interactive=None)
        assert result is True

    @patch("builtins.input", side_effect=EOFError)
    def test_ask_yes_no_eof_error_returns_opposite(self, mock_input: MagicMock):
        """Test ask_yes_no() returns opposite of default on EOFError"""
        result = ask_yes_no("Test question?", default=True, non_interactive=False)
        assert result is False  # Opposite of default=True

        mock_input.side_effect = EOFError
        result = ask_yes_no("Test question?", default=False, non_interactive=False)
        assert result is True  # Opposite of default=False

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_ask_yes_no_keyboard_interrupt_returns_opposite(self, mock_input: MagicMock):
        """Test ask_yes_no() returns opposite of default on KeyboardInterrupt"""
        result = ask_yes_no("Test question?", default=True, non_interactive=False)
        assert result is False  # Opposite of default=True


@pytest.mark.unit
class TestPrintAccessUrls:
    """Tests for print_access_urls() function

    See docs/getting-started.md for usage examples.
    """

    @patch("src.infrastructure.output.print_info")
    @patch("src.infrastructure.output.print_warning")
    @patch("builtins.print")
    def test_print_access_urls_with_nginx(
        self, mock_print: MagicMock, mock_print_warning: MagicMock, mock_print_info: MagicMock
    ):
        """Test print_access_urls() with nginx enabled"""
        print_access_urls(
            local_ip="192.168.1.100",
            use_nginx=True,
            nginx_http_port=8080,
            webui_port="3000",
            litellm_external_port="4000",
        )

        # Check that URLs are printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("192.168.1.100:8080" in str(call) for call in print_calls)
        assert any("192.168.1.100:4000" in str(call) for call in print_calls)

    @patch("src.infrastructure.output.print_info")
    @patch("src.infrastructure.output.print_warning")
    @patch("builtins.print")
    def test_print_access_urls_without_nginx(
        self, mock_print: MagicMock, mock_print_warning: MagicMock, mock_print_info: MagicMock
    ):
        """Test print_access_urls() without nginx"""
        print_access_urls(
            local_ip="192.168.1.100",
            use_nginx=False,
            nginx_http_port=None,
            webui_port="3000",
            litellm_external_port="4000",
        )

        # Check that URLs are printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("192.168.1.100:3000" in str(call) for call in print_calls)
        assert any("192.168.1.100:4000" in str(call) for call in print_calls)

    @patch("src.infrastructure.output.print_info")
    @patch("src.infrastructure.output.print_warning")
    @patch("builtins.print")
    def test_print_access_urls_no_litellm_port(
        self, mock_print: MagicMock, mock_print_warning: MagicMock, mock_print_info: MagicMock
    ):
        """Test print_access_urls() without litellm_external_port"""
        print_access_urls(
            local_ip="192.168.1.100",
            use_nginx=True,
            nginx_http_port=8080,
            webui_port="3000",
            litellm_external_port=None,
        )

        # Check that warning is printed
        mock_print_warning.assert_called()


@pytest.mark.unit
class TestPrintApiInfo:
    """Tests for print_api_info() function

    See docs/getting-started.md for usage examples.
    """

    @patch("src.infrastructure.output.print_info")
    @patch("src.infrastructure.output.print_warning")
    @patch("builtins.print")
    def test_print_api_info_with_virtual_key(
        self, mock_print: MagicMock, mock_print_warning: MagicMock, mock_print_info: MagicMock
    ):
        """Test print_api_info() with virtual key"""
        print_api_info(
            local_ip="192.168.1.100",
            nginx_http_port=8080,
            virtual_key="sk-test-key",
            use_nginx=True,
        )

        # Check that API URL and key are printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("192.168.1.100:8080" in str(call) for call in print_calls)
        assert any("sk-test-key" in str(call) for call in print_calls)

    @patch("src.infrastructure.output.print_info")
    @patch("src.infrastructure.output.print_warning")
    @patch("builtins.print")
    def test_print_api_info_without_virtual_key(
        self, mock_print: MagicMock, mock_print_warning: MagicMock, mock_print_info: MagicMock
    ):
        """Test print_api_info() without virtual key"""
        print_api_info(
            local_ip="192.168.1.100",
            nginx_http_port=8080,
            virtual_key=None,
            use_nginx=True,
        )

        # Check that warning is printed
        mock_print_warning.assert_called()

    @patch("src.infrastructure.output.print_info")
    @patch("src.infrastructure.output.print_warning")
    @patch("builtins.print")
    def test_print_api_info_without_nginx(
        self, mock_print: MagicMock, mock_print_warning: MagicMock, mock_print_info: MagicMock
    ):
        """Test print_api_info() without nginx (should return early)"""
        print_api_info(
            local_ip="192.168.1.100",
            nginx_http_port=None,
            virtual_key="sk-test-key",
            use_nginx=False,
        )

        # Should not print anything
        mock_print.assert_not_called()


@pytest.mark.unit
class TestPrintStatusCommands:
    """Tests for print_status_commands() function

    See docs/getting-started.md for usage examples.
    """

    @patch("src.infrastructure.output.print_info")
    @patch("builtins.print")
    def test_print_status_commands(self, mock_print: MagicMock, mock_print_info: MagicMock):
        """Test print_status_commands() prints status and log commands"""
        print_status_commands()

        # Check that commands are printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("docker compose ps" in str(call) for call in print_calls)
        assert any("docker compose logs" in str(call) for call in print_calls)

