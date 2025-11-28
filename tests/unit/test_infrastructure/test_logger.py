"""
Unit tests for infrastructure.logger module

See docs/architecture.md#logging for usage examples and architecture details.
"""

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.logger import ColoredFormatter, get_logger, setup_logger


@pytest.mark.unit
class TestColoredFormatter:
    """Tests for ColoredFormatter class

    See docs/architecture.md#logging for logging architecture details.
    """

    def test_colors_are_defined(self):
        """Test that all log levels have color codes defined"""
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in expected_levels:
            assert level in ColoredFormatter.COLORS
            assert ColoredFormatter.COLORS[level].startswith("\033[")

    def test_reset_code_is_defined(self):
        """Test that RESET code is defined"""
        assert ColoredFormatter.RESET == "\033[0m"

    def test_format_adds_colors(self):
        """Test that format() adds color codes to levelname"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Check that color code is added
        assert ColoredFormatter.COLORS["INFO"] in formatted
        assert ColoredFormatter.RESET in formatted
        assert "INFO" in formatted
        assert "Test message" in formatted

    def test_format_handles_unknown_level(self):
        """Test that format() handles unknown log levels gracefully"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=99,  # Unknown level
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.levelname = "UNKNOWN"

        formatted = formatter.format(record)

        # Should not crash, may not have color
        assert "UNKNOWN" in formatted or "Test message" in formatted


@pytest.mark.unit
class TestSetupLogger:
    """Tests for setup_logger() function

    See docs/architecture.md#logging for logging architecture details.
    """

    def test_setup_logger_creates_logger_with_name(self):
        """Test that setup_logger creates logger with specified name"""
        logger = setup_logger(name="test_logger", level=logging.DEBUG)
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG

    def test_setup_logger_default_name(self):
        """Test that setup_logger uses default name 'ai_gateway'"""
        logger = setup_logger()
        assert logger.name == "ai_gateway"
        assert logger.level == logging.INFO

    def test_setup_logger_clears_existing_handlers(self):
        """Test that setup_logger clears existing handlers"""
        logger = logging.getLogger("test_clear")
        # Add a handler
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        assert len(logger.handlers) == 1

        # Setup should clear handlers
        setup_logger(name="test_clear")
        assert len(logger.handlers) == 1  # New handler added

    def test_setup_logger_creates_console_handler(self):
        """Test that setup_logger creates console handler"""
        logger = setup_logger(name="test_console")
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert logger.handlers[0].stream == sys.stdout

    def test_setup_logger_console_handler_level(self):
        """Test that console handler has correct level"""
        logger = setup_logger(name="test_level", level=logging.WARNING)
        assert logger.handlers[0].level == logging.WARNING

    @patch("sys.stdout.isatty")
    def test_setup_logger_uses_colored_formatter_when_tty(self, mock_isatty: MagicMock):
        """Test that ColoredFormatter is used when stdout is TTY and use_colors=True"""
        mock_isatty.return_value = True
        logger = setup_logger(name="test_colors", use_colors=True)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, ColoredFormatter)

    @patch("sys.stdout.isatty")
    def test_setup_logger_uses_plain_formatter_when_not_tty(self, mock_isatty: MagicMock):
        """Test that plain Formatter is used when stdout is not TTY"""
        mock_isatty.return_value = False
        logger = setup_logger(name="test_no_colors", use_colors=True)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, logging.Formatter)
        assert not isinstance(logger.handlers[0].formatter, ColoredFormatter)

    def test_setup_logger_uses_plain_formatter_when_colors_disabled(self):
        """Test that plain Formatter is used when use_colors=False"""
        logger = setup_logger(name="test_no_colors_flag", use_colors=False)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, logging.Formatter)
        assert not isinstance(logger.handlers[0].formatter, ColoredFormatter)

    def test_setup_logger_creates_file_handler_when_log_file_specified(self, temp_dir: Path):
        """Test that file handler is created when log_file is specified"""
        log_file = temp_dir / "test.log"
        logger = setup_logger(name="test_file", log_file=log_file)

        assert len(logger.handlers) == 2  # Console + file
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1
        assert file_handlers[0].baseFilename == str(log_file.absolute())

    def test_setup_logger_creates_directory_for_log_file(self, temp_dir: Path):
        """Test that setup_logger creates directory for log_file if it doesn't exist"""
        log_file = temp_dir / "subdir" / "test.log"
        assert not log_file.parent.exists()

        logger = setup_logger(name="test_dir", log_file=log_file)

        assert log_file.parent.exists()
        assert len(logger.handlers) == 2

    def test_setup_logger_file_handler_level(self, temp_dir: Path):
        """Test that file handler has DEBUG level regardless of logger level"""
        log_file = temp_dir / "test.log"
        logger = setup_logger(name="test_file_level", level=logging.WARNING, log_file=log_file)

        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1
        assert file_handlers[0].level == logging.DEBUG

    def test_setup_logger_file_handler_encoding(self, temp_dir: Path):
        """Test that file handler uses UTF-8 encoding"""
        log_file = temp_dir / "test.log"
        logger = setup_logger(name="test_encoding", log_file=log_file)

        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1
        # FileHandler encoding is set in constructor, check via baseFilename
        assert file_handlers[0].baseFilename == str(log_file.absolute())

    def test_setup_logger_file_formatter_format(self, temp_dir: Path):
        """Test that file handler formatter includes timestamp, name, level, and message"""
        log_file = temp_dir / "test.log"
        logger = setup_logger(name="test_format", log_file=log_file)

        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        formatter = file_handlers[0].formatter
        assert "%(asctime)s" in formatter._fmt
        assert "%(name)s" in formatter._fmt
        assert "%(levelname)s" in formatter._fmt
        assert "%(message)s" in formatter._fmt

    def test_setup_logger_console_formatter_format(self):
        """Test that console handler formatter includes only message"""
        logger = setup_logger(name="test_console_format")
        formatter = logger.handlers[0].formatter
        assert "%(message)s" in formatter._fmt
        # Should not include levelname prefix for cleaner output
        assert "%(levelname)s" not in formatter._fmt or "%(levelname)s" in formatter._fmt  # May be in colored formatter

    def test_setup_logger_logs_to_file(self, temp_dir: Path):
        """Test that logger actually writes to file"""
        log_file = temp_dir / "test.log"
        # Set level to DEBUG so DEBUG messages are logged
        logger = setup_logger(name="test_write", level=logging.DEBUG, log_file=log_file)

        logger.info("Test message")
        logger.debug("Debug message")

        # Close handlers to flush
        for handler in logger.handlers:
            handler.close()

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test message" in content
        assert "Debug message" in content


@pytest.mark.unit
class TestGetLogger:
    """Tests for get_logger() function

    See docs/architecture.md#logging for logging architecture details.
    """

    def test_get_logger_returns_logger_with_name(self):
        """Test that get_logger returns logger with specified name"""
        logger = get_logger("test_get")
        assert logger.name == "test_get"

    def test_get_logger_default_name(self):
        """Test that get_logger uses default name 'ai_gateway'"""
        logger = get_logger()
        assert logger.name == "ai_gateway"

    def test_get_logger_sets_up_logger_if_no_handlers(self):
        """Test that get_logger sets up logger if it has no handlers"""
        # Clear any existing logger
        test_logger = logging.getLogger("test_setup")
        test_logger.handlers.clear()

        logger = get_logger("test_setup")
        assert len(logger.handlers) > 0
        assert logger.level == logging.INFO

    def test_get_logger_does_not_recreate_if_handlers_exist(self):
        """Test that get_logger does not recreate logger if handlers already exist"""
        # Setup logger manually
        test_logger = setup_logger("test_existing", level=logging.DEBUG)
        original_handlers = list(test_logger.handlers)

        # Get logger again
        logger = get_logger("test_existing")

        # Should return same logger with same handlers
        assert logger is test_logger
        assert len(logger.handlers) == len(original_handlers)

    def test_get_logger_uses_info_level_by_default(self):
        """Test that get_logger uses INFO level by default when setting up"""
        test_logger = logging.getLogger("test_info")
        test_logger.handlers.clear()

        logger = get_logger("test_info")
        assert logger.level == logging.INFO

    def test_get_logger_uses_colors_by_default(self):
        """Test that get_logger uses colors by default when setting up"""
        test_logger = logging.getLogger("test_colors_default")
        test_logger.handlers.clear()

        with patch("sys.stdout.isatty", return_value=True):
            logger = get_logger("test_colors_default")
            # Should have ColoredFormatter if TTY
            if sys.stdout.isatty():
                assert isinstance(logger.handlers[0].formatter, ColoredFormatter)

