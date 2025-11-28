"""
Structured logging setup
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[34m",  # Blue
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str = "ai_gateway",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Setup structured logger

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        use_colors: Use colored output for console

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if use_colors and sys.stdout.isatty():
        formatter: logging.Formatter = ColoredFormatter(
            "%(message)s",  # Just message, no level prefix for cleaner output
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            "%(message)s",  # Just message, no level prefix for cleaner output
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "ai_gateway") -> logging.Logger:
    """
    Get logger instance.

    See docs/architecture.md#logging for logging details.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    # If logger has no handlers, set it up
    if not logger.handlers:
        logger = setup_logger(name, level=logging.INFO, use_colors=True)
    return logger
