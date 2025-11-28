"""
Pytest configuration and fixtures for E2E tests.

See docs/getting-started.md for system requirements.
See IMPROVEMENT_PLAN.md#Этап-6 for E2E test requirements.
"""

import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Generator, Optional

import pytest
import requests

from src.application.setup_service import SetupService
from src.application.start_service import StartService
from src.infrastructure.docker_client import DockerClient


@pytest.fixture(scope="function")
def e2e_project_root() -> Generator[Path, None, None]:
    """
    Create a temporary project root directory for E2E tests.

    Each test gets its own isolated directory to avoid conflicts.
    Uses unique COMPOSE_PROJECT_NAME for container isolation.
    """
    import uuid
    
    with tempfile.TemporaryDirectory(prefix="ai-gateway-e2e-") as tmpdir:
        project_root = Path(tmpdir)
        
        # Copy necessary files from project root
        # We need docker-compose.yml and other config files
        original_root = Path(__file__).parent.parent.parent
        
        # Copy docker-compose.yml
        if (original_root / "docker-compose.yml").exists():
            shutil.copy2(original_root / "docker-compose.yml", project_root / "docker-compose.yml")
        
        # Copy nginx directory if it exists
        if (original_root / "nginx").exists():
            shutil.copytree(original_root / "nginx", project_root / "nginx")
        
        # Set unique project name for Docker Compose isolation
        # This ensures containers from different tests don't conflict
        unique_id = str(uuid.uuid4())[:8]
        compose_project_name = f"ai-gateway-e2e-{unique_id}"
        os.environ["COMPOSE_PROJECT_NAME"] = compose_project_name
        
        try:
            yield project_root
        finally:
            # Cleanup: stop containers if they're still running
            try:
                docker_client = DockerClient()
                if docker_client.check_daemon_running():
                    # Use the same project name for cleanup
                    os.environ["COMPOSE_PROJECT_NAME"] = compose_project_name
                    docker_client.compose_down(str(project_root), timeout=30)
            except Exception:
                pass  # Ignore cleanup errors
            finally:
                # Clean up environment variable
                if "COMPOSE_PROJECT_NAME" in os.environ:
                    del os.environ["COMPOSE_PROJECT_NAME"]


def _get_e2e_resource_profile() -> Optional[str]:
    """
    Get resource profile for E2E tests.
    
    Priority:
    1. E2E_RESOURCE_PROFILE env var (explicit override)
    2. Default: "small" (for fast tests with minimal resource usage)
    
    E2E tests always use Small VPS by default to:
    - Minimize resource usage (1 worker, ~2.0-2.5GB RAM)
    - Speed up test execution
    - Ensure compatibility with CI/CD environments (GitHub Actions, etc.)
    
    Returns:
        Resource profile name ("small", "medium", "large", "desktop") or None
    """
    # Check explicit override
    e2e_profile = os.environ.get("E2E_RESOURCE_PROFILE", "").lower()
    if e2e_profile in ("small", "medium", "large", "desktop"):
        return e2e_profile
    
    # Default: Small VPS for all E2E tests
    # This ensures fast execution and minimal resource usage
    # Works on both local machines and CI/CD (GitHub Actions, etc.)
    return "small"


@pytest.fixture(scope="function")
def e2e_setup(e2e_project_root: Path) -> Generator[Path, None, None]:
    """
    Run setup in non-interactive mode for E2E tests.
    
    This fixture runs the setup process and generates all necessary config files.
    
    Resource profile selection:
    - If E2E_RESOURCE_PROFILE env var is set, uses that profile
    - Default: "small" (Small VPS - 1 worker, ~2.0-2.5GB RAM)
    
    E2E tests use Small VPS by default for:
    - Fast test execution
    - Minimal resource usage
    - Compatibility with CI/CD environments (GitHub Actions, etc.)
    
    See docs/ci-cd/github-actions-e2e.md for GitHub Actions resource requirements.
    """
    # Set non-interactive mode
    os.environ["NON_INTERACTIVE"] = "1"
    
    # Determine resource profile for E2E tests
    e2e_profile = _get_e2e_resource_profile()
    
    # Override resource profile selection if needed
    original_select = None
    if e2e_profile:
        from src.config import ResourceProfile, select_resource_profile
        from src.infrastructure.output import print_info
        
        # Map profile name to ResourceProfile
        profile_map = {
            "small": ResourceProfile.SMALL_VPS,
            "medium": ResourceProfile.MEDIUM_VPS,
            "large": ResourceProfile.LARGE_VPS,
            "desktop": ResourceProfile.DESKTOP,
        }
        
        target_profile = profile_map.get(e2e_profile)
        if target_profile:
            # Monkey-patch select_resource_profile to return our profile
            original_select = select_resource_profile
            def _select_for_e2e(non_interactive: Optional[bool] = None):
                print_info(f"E2E tests: using {e2e_profile} resource profile (fast tests, minimal resources)")
                return target_profile
            
            # Temporarily replace the function
            import src.config as config_module
            config_module.select_resource_profile = _select_for_e2e
    
    try:
        setup_service = SetupService(e2e_project_root)
        setup_service.run_setup(non_interactive=True)
        
        yield e2e_project_root
    finally:
        # Restore original function if we patched it
        if original_select:
            import src.config as config_module
            config_module.select_resource_profile = original_select
        
        # Cleanup
        if "NON_INTERACTIVE" in os.environ:
            del os.environ["NON_INTERACTIVE"]


@pytest.fixture(scope="function")
def e2e_containers(e2e_setup: Path) -> Generator[Path, None, None]:
    """
    Start containers and wait for them to become healthy.
    
    This fixture starts all containers and waits for health checks.
    Containers are automatically stopped after the test.
    """
    start_service = StartService(e2e_setup)
    
    # Start containers
    if not start_service.start_containers(wait_for_healthy=True):
        pytest.fail("Failed to start containers")
    
    # Wait a bit for services to be fully ready
    time.sleep(5)
    
    yield e2e_setup
    
    # Cleanup: stop containers
    try:
        docker_client = DockerClient()
        docker_client.compose_down(str(e2e_setup), timeout=60)
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
def docker_available() -> bool:
    """
    Check if Docker is available and running.
    
    Skips tests if Docker is not available.
    """
    docker_client = DockerClient()
    is_available, _ = docker_client.check_available()
    is_running = docker_client.check_daemon_running()
    
    if not is_available or not is_running:
        pytest.skip("Docker is not available or not running")
    
    return True


def get_litellm_url(project_root: Path, use_nginx: bool = True) -> str:
    """
    Get LiteLLM base URL for API requests.
    
    Args:
        project_root: Project root directory
        use_nginx: Whether Nginx is enabled
        
    Returns:
        Base URL for LiteLLM API
    """
    from src.application.services import ConfigService
    
    config_service = ConfigService(project_root)
    config_service.load_from_env()
    config = config_service.get_config()
    
    if use_nginx and config.port_config.nginx_http_port:
        return f"http://localhost:{config.port_config.nginx_http_port}/api/litellm/v1"
    elif config.port_config.litellm_external_port:
        return f"http://localhost:{config.port_config.litellm_external_port}/v1"
    else:
        return "http://localhost:4000/v1"


def get_master_key(project_root: Path) -> Optional[str]:
    """
    Get LiteLLM master key from .env file.
    
    Args:
        project_root: Project root directory
        
    Returns:
        Master key or None if not found
    """
    from src.application.services import ConfigService
    
    config_service = ConfigService(project_root)
    return config_service.get_master_key()


def wait_for_http_endpoint(url: str, timeout: int = 60, interval: int = 2) -> bool:
    """
    Wait for HTTP endpoint to become available.
    
    Args:
        url: URL to check
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds
        
    Returns:
        True if endpoint is available, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:  # Accept 2xx, 3xx, 4xx (not 5xx)
                return True
        except requests.RequestException:
            pass
        
        time.sleep(interval)
    
    return False

