"""
Unit tests for infrastructure.file_repository module

See docs/architecture.md#file-operations for usage examples.
"""

import stat
from pathlib import Path

import pytest

from src.core.exceptions import FileOperationError
from src.infrastructure.file_repository import FileRepository


@pytest.mark.unit
class TestFileRepositoryInit:
    """Tests for FileRepository.__init__"""

    def test_init_creates_base_directory(self, temp_dir: Path):
        """Test that __init__ creates base directory if it doesn't exist"""
        base_path = temp_dir / "new_dir"
        assert not base_path.exists()

        repo = FileRepository(base_path)
        assert base_path.exists()
        assert repo.base_path == base_path

    def test_init_with_existing_directory(self, temp_dir: Path):
        """Test that __init__ works with existing directory"""
        base_path = temp_dir / "existing_dir"
        base_path.mkdir()

        repo = FileRepository(base_path)
        assert base_path.exists()
        assert repo.base_path == base_path

    def test_init_with_nested_path(self, temp_dir: Path):
        """Test that __init__ creates nested directories"""
        base_path = temp_dir / "nested" / "deep" / "path"
        assert not base_path.exists()

        repo = FileRepository(base_path)
        assert base_path.exists()
        assert repo.base_path == base_path


@pytest.mark.unit
class TestFileRepositoryReadText:
    """Tests for FileRepository.read_text()"""

    def test_read_text_success(self, temp_dir: Path):
        """Test successful reading of text file"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        content = "Hello, World!\nTest content"

        # Write file first
        (temp_dir / test_file).write_text(content)

        result = repo.read_text(test_file)
        assert result == content

    def test_read_text_with_encoding(self, temp_dir: Path):
        """Test reading file with specific encoding"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        content = "Привет, Мир!"  # Russian text

        (temp_dir / test_file).write_text(content, encoding="utf-8")

        result = repo.read_text(test_file, encoding="utf-8")
        assert result == content

    def test_read_text_relative_path(self, temp_dir: Path):
        """Test reading file with relative path"""
        repo = FileRepository(temp_dir)
        test_file = Path("subdir") / "test.txt"
        content = "Nested content"

        (temp_dir / test_file).parent.mkdir()
        (temp_dir / test_file).write_text(content)

        result = repo.read_text(test_file)
        assert result == content

    def test_read_text_file_not_found(self, temp_dir: Path):
        """Test that read_text raises FileOperationError for missing file"""
        repo = FileRepository(temp_dir)
        test_file = Path("nonexistent.txt")

        with pytest.raises(FileOperationError) as exc_info:
            repo.read_text(test_file)

        assert "Cannot read file" in str(exc_info.value)
        assert str(test_file) in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, (OSError, FileNotFoundError))

    def test_read_text_invalid_encoding(self, temp_dir: Path):
        """Test that read_text raises FileOperationError for invalid encoding"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")

        # Write binary data that can't be decoded as UTF-8
        (temp_dir / test_file).write_bytes(b"\xff\xfe\x00\x01")

        with pytest.raises(FileOperationError) as exc_info:
            repo.read_text(test_file, encoding="utf-8")

        assert "Cannot read file" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, UnicodeDecodeError)


@pytest.mark.unit
class TestFileRepositoryWriteText:
    """Tests for FileRepository.write_text()"""

    def test_write_text_success(self, temp_dir: Path):
        """Test successful writing of text file"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        content = "Hello, World!\nTest content"

        repo.write_text(test_file, content)

        assert (temp_dir / test_file).exists()
        assert (temp_dir / test_file).read_text() == content

    def test_write_text_with_encoding(self, temp_dir: Path):
        """Test writing file with specific encoding"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        content = "Привет, Мир!"  # Russian text

        repo.write_text(test_file, content, encoding="utf-8")

        assert (temp_dir / test_file).read_text(encoding="utf-8") == content

    def test_write_text_creates_directories(self, temp_dir: Path):
        """Test that write_text creates parent directories when create_dirs=True"""
        repo = FileRepository(temp_dir)
        test_file = Path("nested") / "deep" / "test.txt"
        content = "Nested content"

        repo.write_text(test_file, content, create_dirs=True)

        assert (temp_dir / test_file).exists()
        assert (temp_dir / test_file).read_text() == content

    def test_write_text_without_creating_directories(self, temp_dir: Path):
        """Test that write_text doesn't create directories when create_dirs=False"""
        repo = FileRepository(temp_dir)
        test_file = Path("nonexistent") / "test.txt"
        content = "Content"

        # Should raise error if directory doesn't exist
        with pytest.raises(FileOperationError) as exc_info:
            repo.write_text(test_file, content, create_dirs=False)

        assert "Cannot write file" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, (OSError, FileNotFoundError))

    def test_write_text_overwrites_existing_file(self, temp_dir: Path):
        """Test that write_text overwrites existing file"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        original_content = "Original"
        new_content = "New content"

        # Write original file
        (temp_dir / test_file).write_text(original_content)

        # Overwrite with new content
        repo.write_text(test_file, new_content)

        assert (temp_dir / test_file).read_text() == new_content


@pytest.mark.unit
class TestFileRepositoryExists:
    """Tests for FileRepository.exists()"""

    def test_exists_returns_true_for_existing_file(self, temp_dir: Path):
        """Test that exists() returns True for existing file"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")

        (temp_dir / test_file).write_text("content")

        assert repo.exists(test_file) is True

    def test_exists_returns_false_for_nonexistent_file(self, temp_dir: Path):
        """Test that exists() returns False for nonexistent file"""
        repo = FileRepository(temp_dir)
        test_file = Path("nonexistent.txt")

        assert repo.exists(test_file) is False

    def test_exists_returns_true_for_directory(self, temp_dir: Path):
        """Test that exists() returns True for directory (Path.exists() returns True for both files and dirs)"""
        repo = FileRepository(temp_dir)
        test_dir = Path("test_dir")

        (temp_dir / test_dir).mkdir()

        # exists() uses Path.exists() which returns True for both files and directories
        assert repo.exists(test_dir) is True


@pytest.mark.unit
class TestFileRepositorySetPermissions:
    """Tests for FileRepository.set_permissions()"""

    def test_set_permissions_success(self, temp_dir: Path):
        """Test successful setting of file permissions"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        (temp_dir / test_file).write_text("content")

        # Set permissions to 0o600 (read/write for owner only)
        repo.set_permissions(test_file, 0o600)

        file_stat = (temp_dir / test_file).stat()
        # Check that permissions match (using stat.S_IMODE to get only permission bits)
        assert stat.S_IMODE(file_stat.st_mode) == 0o600

    def test_set_permissions_default_mode(self, temp_dir: Path):
        """Test that set_permissions uses default mode 0o600"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        (temp_dir / test_file).write_text("content")

        repo.set_permissions(test_file)

        file_stat = (temp_dir / test_file).stat()
        assert stat.S_IMODE(file_stat.st_mode) == 0o600

    def test_set_permissions_different_modes(self, temp_dir: Path):
        """Test setting different permission modes"""
        repo = FileRepository(temp_dir)
        test_file = Path("test.txt")
        (temp_dir / test_file).write_text("content")

        # Test different modes
        for mode in [0o644, 0o755, 0o777]:
            repo.set_permissions(test_file, mode)
            file_stat = (temp_dir / test_file).stat()
            assert stat.S_IMODE(file_stat.st_mode) == mode


@pytest.mark.unit
class TestFileRepositoryReadEnvFile:
    """Tests for FileRepository.read_env_file()"""

    def test_read_env_file_success(self, temp_dir: Path):
        """Test successful reading of .env file"""
        repo = FileRepository(temp_dir)
        env_file = Path(".env")
        env_content = """KEY1=value1
KEY2=value2
KEY3=value3
"""

        (temp_dir / env_file).write_text(env_content)

        result = repo.read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2", "KEY3": "value3"}

    def test_read_env_file_with_comments(self, temp_dir: Path):
        """Test that read_env_file ignores comments"""
        repo = FileRepository(temp_dir)
        env_file = Path(".env")
        env_content = """# This is a comment
KEY1=value1
# Another comment
KEY2=value2
"""

        (temp_dir / env_file).write_text(env_content)

        result = repo.read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}
        assert "#" not in result

    def test_read_env_file_with_empty_lines(self, temp_dir: Path):
        """Test that read_env_file handles empty lines"""
        repo = FileRepository(temp_dir)
        env_file = Path(".env")
        env_content = """KEY1=value1

KEY2=value2

"""

        (temp_dir / env_file).write_text(env_content)

        result = repo.read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_read_env_file_with_whitespace(self, temp_dir: Path):
        """Test that read_env_file trims whitespace from keys and values"""
        repo = FileRepository(temp_dir)
        env_file = Path(".env")
        env_content = """  KEY1  =  value1
KEY2=value2
"""

        (temp_dir / env_file).write_text(env_content)

        result = repo.read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_read_env_file_with_equals_in_value(self, temp_dir: Path):
        """Test that read_env_file handles values with equals sign"""
        repo = FileRepository(temp_dir)
        env_file = Path(".env")
        env_content = """KEY1=value=with=equals
KEY2=normal_value
"""

        (temp_dir / env_file).write_text(env_content)

        result = repo.read_env_file(env_file)

        assert result == {"KEY1": "value=with=equals", "KEY2": "normal_value"}

    def test_read_env_file_nonexistent_file(self, temp_dir: Path):
        """Test that read_env_file returns empty dict for nonexistent file"""
        repo = FileRepository(temp_dir)
        env_file = Path("nonexistent.env")

        result = repo.read_env_file(env_file)

        assert result == {}

    def test_read_env_file_default_path(self, temp_dir: Path):
        """Test that read_env_file uses .env as default path"""
        repo = FileRepository(temp_dir)
        env_content = """KEY1=value1
KEY2=value2
"""

        (temp_dir / ".env").write_text(env_content)

        result = repo.read_env_file()

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_read_env_file_invalid_format(self, temp_dir: Path):
        """Test that read_env_file handles lines without equals sign"""
        repo = FileRepository(temp_dir)
        env_file = Path(".env")
        env_content = """KEY1=value1
INVALID_LINE
KEY2=value2
"""

        (temp_dir / env_file).write_text(env_content)

        result = repo.read_env_file(env_file)

        # Should only include valid lines
        assert result == {"KEY1": "value1", "KEY2": "value2"}
        assert "INVALID_LINE" not in result

