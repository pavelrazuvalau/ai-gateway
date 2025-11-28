"""
Pytest configuration and shared fixtures
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def project_root(temp_dir: Path) -> Path:
    """Create a project root directory for tests"""
    return temp_dir


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Clean environment variables for tests"""
    # Save original values
    original_non_interactive = os.environ.get("NON_INTERACTIVE")

    # Clean up
    if "NON_INTERACTIVE" in os.environ:
        del os.environ["NON_INTERACTIVE"]

    yield

    # Restore original values
    if original_non_interactive is not None:
        os.environ["NON_INTERACTIVE"] = original_non_interactive






