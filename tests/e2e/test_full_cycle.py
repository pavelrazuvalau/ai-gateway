"""
E2E tests for full cycle: setup → start → health checks → stop.

See docs/getting-started.md for system requirements.
See IMPROVEMENT_PLAN.md#Этап-6 for E2E test requirements.
"""

import time
from pathlib import Path

import pytest
import requests

from src.application.start_service import StartService
from src.infrastructure.docker_client import DockerClient
from tests.e2e.conftest import get_litellm_url, get_master_key, wait_for_http_endpoint


@pytest.mark.e2e
class TestFullCycle:
    """
    Test full cycle: setup → start → health checks → HTTP endpoints → stop.
    
    See docs/getting-started.md#step-1-run-setup-script for setup details.
    See docs/getting-started.md#step-2-start-the-system for startup details.
    See docs/troubleshooting.md#containers-wont-start for health check details.
    """

    def test_setup_completes_successfully(self, e2e_setup: Path, docker_available: bool) -> None:
        """
        Test that setup completes successfully in non-interactive mode.
        
        See docs/getting-started.md#step-1-run-setup-script for setup details.
        """
        # Check that .env file was created
        env_file = e2e_setup / ".env"
        assert env_file.exists(), ".env file should be created during setup"
        
        # Check that config.yaml was created
        config_file = e2e_setup / "config.yaml"
        assert config_file.exists(), "config.yaml should be created during setup"
        
        # Check that docker-compose.override.yml was created
        override_file = e2e_setup / "docker-compose.override.yml"
        assert override_file.exists(), "docker-compose.override.yml should be created during setup"

    def test_containers_start_and_become_healthy(
        self, e2e_containers: Path, docker_available: bool
    ) -> None:
        """
        Test that containers start and become healthy.
        
        See docs/troubleshooting.md#containers-wont-start for health check details.
        See docs/getting-started.md#step-2-start-the-system for startup details.
        """
        docker_client = DockerClient()
        start_service = StartService(e2e_containers)
        
        # Check container status
        has_errors, errors = start_service.check_container_status()
        
        if has_errors:
            pytest.fail(f"Containers have errors: {errors}")
        
        # Verify containers are running
        # get_running_containers returns a list of container name strings, not dicts
        # Don't use filter_name - it filters by name pattern, not by project directory
        container_names = docker_client.get_running_containers()
        
        # Debug: print container names if assertion fails
        if not any("litellm-proxy" in name or name == "litellm-proxy" for name in container_names):
            print(f"DEBUG: Available container names: {container_names}")
        
        # Check for expected containers (using exact names from docker-compose.yml)
        assert any("litellm-proxy" in name or name == "litellm-proxy" for name in container_names), f"LiteLLM container should be running. Found: {container_names}"
        assert any("litellm-postgres" in name or name == "litellm-postgres" for name in container_names), f"PostgreSQL container should be running. Found: {container_names}"
        assert any("open-webui" in name or name == "open-webui" for name in container_names), f"Open WebUI container should be running. Found: {container_names}"

    def test_litellm_health_endpoint(
        self, e2e_containers: Path, docker_available: bool
    ) -> None:
        """
        Test that LiteLLM health endpoint is accessible.
        
        See docs/troubleshooting.md#containers-wont-start for health check details.
        """
        # Get LiteLLM URL (direct, not through Nginx)
        from src.application.services import ConfigService
        
        config_service = ConfigService(e2e_containers)
        config_service.load_from_env()
        config = config_service.get_config()
        
        # Try direct LiteLLM port first
        if config.port_config.litellm_external_port:
            litellm_url = f"http://localhost:{config.port_config.litellm_external_port}"
        else:
            litellm_url = "http://localhost:4000"
        
        health_url = f"{litellm_url}/health/liveliness"
        
        # Wait for endpoint to be available
        assert wait_for_http_endpoint(health_url, timeout=120), "LiteLLM health endpoint should be accessible"
        
        # Check health endpoint
        response = requests.get(health_url, timeout=10)
        assert response.status_code == 200, f"Health endpoint should return 200, got {response.status_code}"

    def test_litellm_api_endpoints(
        self, e2e_containers: Path, docker_available: bool
    ) -> None:
        """
        Test that LiteLLM API endpoints are accessible.
        
        See docs/integrations/api-for-agents.md#api-endpoints for API details.
        """
        master_key = get_master_key(e2e_containers)
        assert master_key, "Master key should be available"
        
        # Get LiteLLM API URL
        litellm_url = get_litellm_url(e2e_containers, use_nginx=True)
        
        # Wait for API to be available
        models_url = f"{litellm_url}/models"
        assert wait_for_http_endpoint(models_url, timeout=120), "LiteLLM API should be accessible"
        
        # Test /v1/models endpoint
        headers = {"Authorization": f"Bearer {master_key}"}
        response = requests.get(models_url, headers=headers, timeout=10)
        
        assert response.status_code == 200, f"Models endpoint should return 200, got {response.status_code}"
        
        data = response.json()
        assert "data" in data, "Response should contain 'data' field"
        assert isinstance(data["data"], list), "Response data should be a list"

    def test_open_webui_endpoint(
        self, e2e_containers: Path, docker_available: bool
    ) -> None:
        """
        Test that Open WebUI endpoint is accessible.
        
        See docs/getting-started.md#step-2-start-the-system for access details.
        """
        from src.application.services import ConfigService
        
        config_service = ConfigService(e2e_containers)
        config_service.load_from_env()
        config = config_service.get_config()
        
        # Get Open WebUI URL
        if config.port_config.nginx_http_port:
            webui_url = f"http://localhost:{config.port_config.nginx_http_port}"
        else:
            webui_url = "http://localhost:3000"
        
        # Wait for endpoint to be available
        assert wait_for_http_endpoint(webui_url, timeout=120), "Open WebUI should be accessible"
        
        # Check Open WebUI endpoint (should return HTML or redirect)
        response = requests.get(webui_url, timeout=10, allow_redirects=False)
        assert response.status_code in (200, 301, 302), f"Open WebUI should be accessible, got {response.status_code}"

    def test_containers_stop_successfully(
        self, e2e_setup: Path, docker_available: bool
    ) -> None:
        """
        Test that containers can be stopped successfully.
        
        See docs/getting-started.md for stop details.
        """
        docker_client = DockerClient()
        start_service = StartService(e2e_setup)
        
        # Start containers
        assert start_service.start_containers(wait_for_healthy=True), "Containers should start successfully"
        
        # Wait a bit for services to be ready
        time.sleep(5)
        
        # Stop containers
        docker_client.compose_down(str(e2e_setup), timeout=60)
        
        # Verify containers are stopped
        containers = docker_client.get_running_containers(str(e2e_setup))
        container_names = [c.get("Name", "") for c in containers]
        
        # Check that no containers from our project are running
        # (containers from other tests might be running, so we check by project name)
        project_containers = [name for name in container_names if "litellm" in name.lower()]
        assert len(project_containers) == 0, f"Containers should be stopped, but found: {project_containers}"

