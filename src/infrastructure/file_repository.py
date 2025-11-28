"""
File system operations abstraction (Repository pattern)
"""

import os
from pathlib import Path
from typing import Dict

from ..core.exceptions import FileOperationError
from ..infrastructure.logger import get_logger

logger = get_logger(__name__)


class FileRepository:
    """
    Repository for file operations (Repository pattern).

    Provides abstraction for file system operations.
    """

    def __init__(self, base_path: Path):
        """
        Initialize file repository

        Args:
            base_path: Base directory for operations
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def read_text(self, file_path: Path, encoding: str = "utf-8") -> str:
        """
        Read text file

        Args:
            file_path: Path to file (relative to base_path)
            encoding: File encoding

        Returns:
            File contents

        Raises:
            FileOperationError: If file cannot be read
        """
        full_path = self.base_path / file_path
        try:
            with open(full_path, encoding=encoding) as f:
                return f.read()
        except (OSError, UnicodeDecodeError) as e:
            logger.error(
                f"Failed to read file {full_path}: {e}",
                exc_info=True,
                extra={"file_path": str(file_path), "full_path": str(full_path)},
            )
            raise FileOperationError(f"Cannot read file {file_path}: {e}") from e

    def write_text(
        self,
        file_path: Path,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> None:
        """
        Write text file

        Args:
            file_path: Path to file (relative to base_path)
            content: Content to write
            encoding: File encoding
            create_dirs: Create parent directories if needed

        Raises:
            FileOperationError: If file cannot be written
        """
        full_path = self.base_path / file_path
        if create_dirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, "w", encoding=encoding) as f:
                f.write(content)
            logger.debug(f"Written file {full_path}")
        except (OSError, PermissionError) as e:
            logger.error(
                f"Failed to write file {full_path}: {e}",
                exc_info=True,
                extra={"file_path": str(file_path), "full_path": str(full_path)},
            )
            raise FileOperationError(f"Cannot write file {file_path}: {e}") from e

    def exists(self, file_path: Path) -> bool:
        """Check if file exists"""
        return (self.base_path / file_path).exists()

    def set_permissions(self, file_path: Path, mode: int = 0o600) -> None:
        """
        Set file permissions

        Args:
            file_path: Path to file
            mode: Permission mode (octal)
        """
        full_path = self.base_path / file_path
        try:
            os.chmod(full_path, mode)
            logger.debug(f"Set permissions {oct(mode)} on {full_path}")
        except (OSError, PermissionError) as e:
            logger.warning(f"Failed to set permissions on {full_path}: {e}")

    def read_env_file(self, file_path: Path = Path(".env")) -> Dict[str, str]:
        """
        Read .env file and return as dictionary

        Args:
            file_path: Path to .env file

        Returns:
            Dictionary of environment variables
        """
        env_vars: Dict[str, str] = {}
        if not self.exists(file_path):
            return env_vars

        try:
            content = self.read_text(file_path)
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
        except FileOperationError:
            logger.warning(f"Could not read env file {file_path}")

        return env_vars
