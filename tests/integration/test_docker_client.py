"""
Integration tests for DockerClient.

See docs/troubleshooting.md#containers-wont-start for troubleshooting.
See docs/getting-started.md#step-2-start-the-system for startup details.
"""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.core.exceptions import DockerError
from src.infrastructure.docker_client import DockerClient


class TestDockerClientCheckAvailable:
    """Test Docker availability checks."""

    @patch("subprocess.run")
    def test_check_available_success(self, mock_run: MagicMock):
        """Test checking Docker availability when Docker is available."""
        mock_result = MagicMock()
        mock_result.stdout = "Docker version 24.0.0, build abc123\n"
        mock_run.return_value = mock_result

        is_available, version = DockerClient.check_available()

        assert is_available is True
        assert version == "Docker version 24.0.0, build abc123"
        mock_run.assert_called_once_with(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )

    @patch("subprocess.run")
    def test_check_available_not_found(self, mock_run: MagicMock):
        """Test checking Docker availability when Docker is not installed."""
        mock_run.side_effect = FileNotFoundError("docker: command not found")

        is_available, version = DockerClient.check_available()

        assert is_available is False
        assert version is None

    @patch("subprocess.run")
    def test_check_available_process_error(self, mock_run: MagicMock):
        """Test checking Docker availability when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")

        is_available, version = DockerClient.check_available()

        assert is_available is False
        assert version is None

    @patch("subprocess.run")
    def test_check_available_timeout(self, mock_run: MagicMock):
        """Test checking Docker availability when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker", 5)

        is_available, version = DockerClient.check_available()

        assert is_available is False
        assert version is None


class TestDockerClientCheckDaemonRunning:
    """Test Docker daemon running checks."""

    @patch("subprocess.run")
    def test_check_daemon_running_success(self, mock_run: MagicMock):
        """Test checking if Docker daemon is running when it is."""
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        is_running = DockerClient.check_daemon_running()

        assert is_running is True
        mock_run.assert_called_once_with(
            ["docker", "ps"],
            capture_output=True,
            check=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_check_daemon_running_not_running(self, mock_run: MagicMock):
        """Test checking if Docker daemon is running when it is not."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")

        is_running = DockerClient.check_daemon_running()

        assert is_running is False

    @patch("subprocess.run")
    def test_check_daemon_running_not_found(self, mock_run: MagicMock):
        """Test checking if Docker daemon is running when Docker is not installed."""
        mock_run.side_effect = FileNotFoundError("docker: command not found")

        is_running = DockerClient.check_daemon_running()

        assert is_running is False

    @patch("subprocess.run")
    def test_check_daemon_running_timeout(self, mock_run: MagicMock):
        """Test checking if Docker daemon is running when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker", 5)

        is_running = DockerClient.check_daemon_running()

        assert is_running is False


class TestDockerClientCheckComposeAvailable:
    """Test Docker Compose availability checks."""

    @patch("subprocess.run")
    def test_check_compose_available_v2(self, mock_run: MagicMock):
        """Test checking Docker Compose availability when v2 is available."""
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        is_available = DockerClient.check_compose_available()

        assert is_available is True
        # Should try docker compose first (v2)
        mock_run.assert_called_with(
            ["docker", "compose", "version"],
            capture_output=True,
            check=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_check_compose_available_v1(self, mock_run: MagicMock):
        """Test checking Docker Compose availability when only v1 is available."""
        # First call (v2) fails, second call (v1) succeeds
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, "docker compose"),
            MagicMock(),  # v1 succeeds
        ]

        is_available = DockerClient.check_compose_available()

        assert is_available is True
        # Should try docker-compose (v1) after v2 fails
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_check_compose_available_not_found(self, mock_run: MagicMock):
        """Test checking Docker Compose availability when not available."""
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, "docker compose"),
            FileNotFoundError("docker-compose: command not found"),
        ]

        is_available = DockerClient.check_compose_available()

        assert is_available is False


class TestDockerClientGetRunningContainers:
    """Test getting running containers."""

    @patch("subprocess.run")
    def test_get_running_containers_success(self, mock_run: MagicMock):
        """Test getting running containers successfully."""
        mock_result = MagicMock()
        mock_result.stdout = "container1\ncontainer2\ncontainer3\n"
        mock_run.return_value = mock_result

        containers = DockerClient.get_running_containers()

        assert containers == ["container1", "container2", "container3"]
        mock_run.assert_called_once_with(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_get_running_containers_with_filter(self, mock_run: MagicMock):
        """Test getting running containers with name filter."""
        mock_result = MagicMock()
        mock_result.stdout = "ai-gateway-litellm\n"
        mock_run.return_value = mock_result

        containers = DockerClient.get_running_containers(filter_name="ai-gateway")

        assert containers == ["ai-gateway-litellm"]
        mock_run.assert_called_once_with(
            ["docker", "ps", "--format", "{{.Names}}", "--filter", "name=ai-gateway"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_get_running_containers_empty(self, mock_run: MagicMock):
        """Test getting running containers when none are running."""
        mock_result = MagicMock()
        mock_result.stdout = "\n"
        mock_run.return_value = mock_result

        containers = DockerClient.get_running_containers()

        assert containers == []

    @patch("subprocess.run")
    def test_get_running_containers_error(self, mock_run: MagicMock):
        """Test getting running containers when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")

        containers = DockerClient.get_running_containers()

        # Should return empty list instead of raising exception
        assert containers == []

    @patch("subprocess.run")
    def test_get_running_containers_not_found(self, mock_run: MagicMock):
        """Test getting running containers when Docker is not installed."""
        mock_run.side_effect = FileNotFoundError("docker: command not found")

        containers = DockerClient.get_running_containers()

        assert containers == []


class TestDockerClientComposeDown:
    """Test docker compose down."""

    @patch("subprocess.run")
    def test_compose_down_success(self, mock_run: MagicMock, temp_dir):
        """Test stopping containers successfully."""
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        DockerClient.compose_down(str(temp_dir))

        mock_run.assert_called_once_with(
            ["docker", "compose", "down"],
            cwd=str(temp_dir),
            check=True,
            timeout=30,
        )

    @patch("subprocess.run")
    def test_compose_down_error(self, mock_run: MagicMock, temp_dir):
        """Test stopping containers when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker compose")

        with pytest.raises(DockerError, match="Cannot stop containers"):
            DockerClient.compose_down(str(temp_dir))

    @patch("subprocess.run")
    def test_compose_down_timeout(self, mock_run: MagicMock, temp_dir):
        """Test stopping containers when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker compose", 30)

        with pytest.raises(DockerError, match="Cannot stop containers"):
            DockerClient.compose_down(str(temp_dir))


class TestDockerClientComposeUp:
    """Test docker compose up."""

    @patch("subprocess.run")
    def test_compose_up_detached(self, mock_run: MagicMock, temp_dir):
        """Test starting containers in detached mode."""
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        DockerClient.compose_up(str(temp_dir), detach=True, wait=False)

        mock_run.assert_called_once_with(
            ["docker", "compose", "up", "-d"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            check=True,
            timeout=360,
        )

    @patch("subprocess.run")
    def test_compose_up_with_wait(self, mock_run: MagicMock, temp_dir):
        """Test starting containers with wait for health checks."""
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        DockerClient.compose_up(str(temp_dir), detach=True, wait=True)

        mock_run.assert_called_once_with(
            ["docker", "compose", "up", "-d", "--wait", "--wait-timeout", "300"],
            cwd=str(temp_dir),
            check=True,
            timeout=2160,  # 360 * 6
        )

    @patch("subprocess.run")
    def test_compose_up_not_detached(self, mock_run: MagicMock, temp_dir):
        """Test starting containers in foreground mode."""
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        DockerClient.compose_up(str(temp_dir), detach=False, wait=False)

        mock_run.assert_called_once_with(
            ["docker", "compose", "up"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            check=True,
            timeout=360,
        )

    @patch("subprocess.run")
    def test_compose_up_error(self, mock_run: MagicMock, temp_dir):
        """Test starting containers when command fails."""
        mock_error = subprocess.CalledProcessError(1, "docker compose", stderr="Error")
        mock_run.side_effect = mock_error

        with pytest.raises(DockerError, match="Cannot start containers"):
            DockerClient.compose_up(str(temp_dir))

    @patch("subprocess.run")
    def test_compose_up_timeout(self, mock_run: MagicMock, temp_dir):
        """Test starting containers when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker compose", 360)

        with pytest.raises(DockerError, match="Cannot start containers: timeout"):
            DockerClient.compose_up(str(temp_dir))


class TestDockerClientWaitForContainers:
    """Test waiting for containers to become healthy."""

    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_containers_healthy(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_run: MagicMock, temp_dir
    ):
        """Test waiting for containers when they become healthy."""
        # Mock time to simulate waiting
        mock_time.side_effect = [0, 1]  # Start at 0, then 1 second later

        # Mock container status - all healthy
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "Service": "litellm",
                "State": "running",
                "Health": "healthy",
            }
        )
        mock_run.return_value = mock_result

        result = DockerClient.wait_for_containers(str(temp_dir), timeout=300)

        assert result is True
        mock_run.assert_called()

    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_containers_running_no_healthcheck(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_run: MagicMock, temp_dir
    ):
        """Test waiting for containers when they are running without healthcheck."""
        mock_time.side_effect = [0, 1]

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "Service": "litellm",
                "State": "running",
                "Health": "",  # No healthcheck
            }
        )
        mock_run.return_value = mock_result

        result = DockerClient.wait_for_containers(str(temp_dir), timeout=300)

        assert result is True

    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_containers_timeout(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_run: MagicMock, temp_dir
    ):
        """Test waiting for containers when timeout is reached."""
        # Simulate timeout - time starts at 0, then exceeds timeout
        mock_time.side_effect = [0, 301]  # Exceeds 300 second timeout

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "Service": "litellm",
                "State": "starting",
                "Health": "",
            }
        )
        mock_run.return_value = mock_result

        result = DockerClient.wait_for_containers(str(temp_dir), timeout=300)

        assert result is False

    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_containers_unhealthy(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_run: MagicMock, temp_dir
    ):
        """Test waiting for containers when they are unhealthy."""
        # time.time() is called multiple times in the loop
        # First call: start_time = 0
        # Subsequent calls in loop: should exceed timeout to exit
        mock_time.side_effect = [0, 1, 301]  # Start at 0, then 1, then timeout

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "Service": "litellm",
                "State": "running",
                "Health": "unhealthy",
            }
        )
        mock_run.return_value = mock_result

        result = DockerClient.wait_for_containers(str(temp_dir), timeout=300)

        assert result is False

    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_containers_empty(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_run: MagicMock, temp_dir
    ):
        """Test waiting for containers when no containers are found."""
        mock_time.side_effect = [0, 1]

        mock_result = MagicMock()
        mock_result.stdout = ""  # No containers
        mock_run.return_value = mock_result

        # Should continue waiting (return False after timeout)
        mock_time.side_effect = [0, 301]  # Timeout
        result = DockerClient.wait_for_containers(str(temp_dir), timeout=300)

        assert result is False


class TestDockerClientGetContainerLogs:
    """Test getting container logs."""

    @patch("subprocess.run")
    def test_get_container_logs_success(self, mock_run: MagicMock, temp_dir):
        """Test getting container logs successfully."""
        mock_result = MagicMock()
        mock_result.stdout = "Log line 1\nLog line 2\nLog line 3\n"
        mock_run.return_value = mock_result

        logs = DockerClient.get_container_logs(str(temp_dir), "litellm", tail=50)

        assert "Log line 1" in logs
        assert "Log line 2" in logs
        assert "Log line 3" in logs
        mock_run.assert_called_once_with(
            ["docker", "compose", "logs", "--tail", "50", "litellm"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

    @patch("subprocess.run")
    def test_get_container_logs_custom_tail(self, mock_run: MagicMock, temp_dir):
        """Test getting container logs with custom tail value."""
        mock_result = MagicMock()
        mock_result.stdout = "Recent logs\n"
        mock_run.return_value = mock_result

        logs = DockerClient.get_container_logs(str(temp_dir), "litellm", tail=100)

        assert "Recent logs" in logs
        mock_run.assert_called_once_with(
            ["docker", "compose", "logs", "--tail", "100", "litellm"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

    @patch("subprocess.run")
    def test_get_container_logs_error(self, mock_run: MagicMock, temp_dir):
        """Test getting container logs when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker compose")

        logs = DockerClient.get_container_logs(str(temp_dir), "litellm")

        # Should return error message instead of raising exception
        assert "Failed to retrieve logs" in logs

    @patch("subprocess.run")
    def test_get_container_logs_timeout(self, mock_run: MagicMock, temp_dir):
        """Test getting container logs when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker compose", 30)

        logs = DockerClient.get_container_logs(str(temp_dir), "litellm")

        assert "Failed to retrieve logs" in logs


class TestDockerClientGetFailedContainers:
    """Test getting failed containers."""

    @patch("subprocess.run")
    def test_get_failed_containers_success(self, mock_run: MagicMock, temp_dir):
        """Test getting failed containers successfully."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "Service": "litellm",
                "State": "exited",
                "ExitCode": 1,
                "Status": "Exited (1) 2 minutes ago",
            }
        )
        mock_run.return_value = mock_result

        failed = DockerClient.get_failed_containers(str(temp_dir))

        assert len(failed) == 1
        assert failed[0]["name"] == "litellm"
        assert failed[0]["state"] == "exited"
        assert failed[0]["exit_code"] == 1
        mock_run.assert_called_once_with(
            ["docker", "compose", "ps", "-a", "--format", "json"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

    @patch("subprocess.run")
    def test_get_failed_containers_multiple(self, mock_run: MagicMock, temp_dir):
        """Test getting multiple failed containers."""
        mock_result = MagicMock()
        # Multiple containers, some failed
        mock_result.stdout = "\n".join(
            [
                json.dumps(
                    {
                        "Service": "litellm",
                        "State": "exited",
                        "ExitCode": 1,
                        "Status": "Exited (1)",
                    }
                ),
                json.dumps(
                    {
                        "Service": "open-webui",
                        "State": "running",
                        "ExitCode": 0,
                        "Status": "Up 5 minutes",
                    }
                ),
                json.dumps(
                    {
                        "Service": "postgres",
                        "State": "dead",
                        "ExitCode": 137,
                        "Status": "Dead",
                    }
                ),
            ]
        )
        mock_run.return_value = mock_result

        failed = DockerClient.get_failed_containers(str(temp_dir))

        assert len(failed) == 2  # litellm and postgres
        assert failed[0]["name"] == "litellm"
        assert failed[1]["name"] == "postgres"

    @patch("subprocess.run")
    def test_get_failed_containers_empty(self, mock_run: MagicMock, temp_dir):
        """Test getting failed containers when none are failed."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "Service": "litellm",
                "State": "running",
                "ExitCode": 0,
                "Status": "Up 5 minutes",
            }
        )
        mock_run.return_value = mock_result

        failed = DockerClient.get_failed_containers(str(temp_dir))

        assert failed == []

    @patch("subprocess.run")
    def test_get_failed_containers_no_containers(self, mock_run: MagicMock, temp_dir):
        """Test getting failed containers when no containers exist."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        failed = DockerClient.get_failed_containers(str(temp_dir))

        assert failed == []

    @patch("subprocess.run")
    def test_get_failed_containers_error(self, mock_run: MagicMock, temp_dir):
        """Test getting failed containers when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker compose")

        failed = DockerClient.get_failed_containers(str(temp_dir))

        # Should return empty list instead of raising exception
        assert failed == []

    @patch("subprocess.run")
    def test_get_failed_containers_invalid_json(self, mock_run: MagicMock, temp_dir):
        """Test getting failed containers when JSON is invalid."""
        mock_result = MagicMock()
        mock_result.stdout = "invalid json\n"
        mock_run.return_value = mock_result

        failed = DockerClient.get_failed_containers(str(temp_dir))

        # Should skip invalid JSON and return empty list
        assert failed == []

