"""
Docker operations abstraction.

See docs/troubleshooting.md#containers-wont-start for troubleshooting.
See docs/getting-started.md#step-2-start-the-system for startup details.
"""

import subprocess
from typing import List, Optional, Tuple

from ..core.constants import (
    DOCKER_DOWN_TIMEOUT,
    DOCKER_TIMEOUT,
    DOCKER_UP_TIMEOUT,
)
from ..core.exceptions import DockerError
from ..infrastructure.logger import get_logger

logger = get_logger(__name__)


class DockerClient:
    """Client for Docker operations"""

    @staticmethod
    def check_available() -> Tuple[bool, Optional[str]]:
        """
        Check if Docker is available

        Returns:
            Tuple of (is_available, version_string)
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=DOCKER_TIMEOUT,
                check=True,
            )
            version = result.stdout.strip()
            logger.debug(f"Docker available: {version}")
            return True, version
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ) as e:
            logger.warning(f"Docker not available: {e}")
            return False, None

    @staticmethod
    def check_daemon_running() -> bool:
        """Check if Docker daemon is running"""
        try:
            subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                check=True,
                timeout=DOCKER_TIMEOUT,
            )
            logger.debug("Docker daemon is running")
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            logger.warning("Docker daemon is not running")
            return False

    @staticmethod
    def check_compose_available() -> bool:
        """Check if Docker Compose is available"""
        # Try docker compose (v2)
        try:
            subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            logger.debug("Docker Compose v2 available")
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            pass

        # Try docker-compose (v1)
        try:
            subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            logger.debug("Docker Compose v1 available")
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            logger.warning("Docker Compose not available")
            return False

    @staticmethod
    def get_running_containers(filter_name: Optional[str] = None) -> List[str]:
        """
        Get list of running containers

        Args:
            filter_name: Optional container name filter

        Returns:
            List of container names (empty list if Docker is unavailable or error occurs)
        """
        try:
            cmd = ["docker", "ps", "--format", "{{.Names}}"]
            if filter_name:
                cmd.extend(["--filter", f"name={filter_name}"])

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=DOCKER_TIMEOUT
            )
            containers = [
                line.strip()
                for line in result.stdout.strip().split("\n")
                if line.strip()
            ]
            logger.debug(f"Found {len(containers)} running containers")
            return containers
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ) as e:
            # Don't raise exception - return empty list instead
            # This allows setup to continue even if Docker is unavailable
            logger.warning(f"Failed to get containers (Docker may be unavailable): {e}")
            # Try to get stderr if available
            if hasattr(e, "stderr") and e.stderr:
                stderr_str = (
                    e.stderr.decode("utf-8")
                    if isinstance(e.stderr, bytes)
                    else str(e.stderr)
                )
                logger.debug(f"Docker error output: {stderr_str}")
            return []

    @staticmethod
    def compose_down(work_dir: str) -> None:
        """
        Run docker compose down

        Args:
            work_dir: Working directory

        Raises:
            DockerError: If command fails
        """
        try:
            subprocess.run(
                ["docker", "compose", "down"],
                cwd=work_dir,
                check=True,
                timeout=DOCKER_DOWN_TIMEOUT,
            )
            logger.info("Docker containers stopped")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(
                f"Failed to stop containers: {e}",
                exc_info=True,
                extra={"work_dir": work_dir},
            )
            raise DockerError(f"Cannot stop containers: {e}") from e

    @staticmethod
    def compose_up(work_dir: str, detach: bool = True, wait: bool = False) -> None:
        """
        Run docker compose up

        Args:
            work_dir: Working directory
            detach: Run in detached mode
            wait: Wait for containers to become healthy (requires Docker Compose v2.3+)

        Raises:
            DockerError: If command fails
        """
        try:
            cmd = ["docker", "compose", "up"]
            if detach:
                cmd.append("-d")
            if wait:
                # --wait waits for containers to be healthy (Docker Compose v2.3+)
                cmd.append("--wait")
                cmd.append("--wait-timeout")
                cmd.append("300")  # 5 minutes timeout for healthchecks

            # Increase timeout if waiting for healthchecks
            timeout = DOCKER_UP_TIMEOUT * 6 if wait else DOCKER_UP_TIMEOUT

            # When using --wait, show output in real-time for better UX
            if wait:
                # Capture stderr to see errors even with --wait
                result = subprocess.run(
                    cmd,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=timeout,
                )
            else:
                result = subprocess.run(
                    cmd,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=timeout,
                )
            logger.info("Docker containers started")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Failed to start containers: {e}",
                exc_info=True,
                extra={"work_dir": work_dir, "wait": wait},
            )
            # Log stderr for debugging (even with --wait, we capture it now)
            if e.stderr:
                logger.error(f"Docker compose stderr: {e.stderr}")
            if e.stdout:
                logger.debug(f"Docker compose stdout: {e.stdout}")
            raise DockerError(f"Cannot start containers: {e.stderr or str(e)}") from e
        except subprocess.TimeoutExpired as e:
            logger.error(
                f"Timeout starting containers: {e}",
                exc_info=True,
                extra={"work_dir": work_dir, "timeout": timeout},
            )
            raise DockerError("Cannot start containers: timeout") from e

    @staticmethod
    def wait_for_containers(work_dir: str, timeout: int = 300) -> bool:
        """
        Wait for containers to become healthy

        Args:
            work_dir: Working directory
            timeout: Maximum time to wait in seconds (default: 300 = 5 minutes)

        Returns:
            True if all containers are healthy, False otherwise
        """
        import time

        logger.info("Waiting for containers to become healthy...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check container status
                result = subprocess.run(
                    ["docker", "compose", "ps", "--format", "json"],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )

                if not result.stdout.strip():
                    # No containers found
                    time.sleep(2)
                    continue

                import json

                containers = []
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        try:
                            containers.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

                if not containers:
                    time.sleep(2)
                    continue

                # Check if all containers are healthy or running
                all_healthy = True
                for container in containers:
                    health = container.get("Health", "")
                    state = container.get("State", "")
                    service = container.get("Service", "")

                    # Skip if container is not part of our stack
                    if not service:
                        continue

                    # Container is healthy if:
                    # - Health is "healthy" (has healthcheck and passed)
                    # - Or State is "running" and no healthcheck is defined (empty health)
                    # - Or State is "healthy" (alternative format)
                    if health:
                        # Has healthcheck - must be "healthy"
                        if health.lower() not in ("healthy", ""):
                            all_healthy = False
                            break
                    elif state.lower() not in ("running", "healthy"):
                        # No healthcheck but must be running
                        all_healthy = False
                        break

                if all_healthy:
                    logger.info("All containers are healthy")
                    return True

                # Wait a bit before checking again
                time.sleep(3)

            except (
                subprocess.CalledProcessError,
                subprocess.TimeoutExpired,
                FileNotFoundError,
            ) as e:
                logger.warning(f"Error checking container status: {e}")
                time.sleep(3)
                continue

        logger.warning(
            f"Timeout waiting for containers to become healthy (waited {timeout}s)"
        )
        return False

    @staticmethod
    def get_container_logs(work_dir: str, container_name: str, tail: int = 50) -> str:
        """
        Get logs from a specific container

        Args:
            work_dir: Working directory
            container_name: Name of the container
            tail: Number of last lines to get (default: 50)

        Returns:
            Container logs as string
        """
        try:
            result = subprocess.run(
                ["docker", "compose", "logs", "--tail", str(tail), container_name],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            return result.stdout
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ) as e:
            logger.warning(f"Failed to get logs for {container_name}: {e}")
            return f"Failed to retrieve logs: {e}"

    @staticmethod
    def get_failed_containers(work_dir: str) -> list[dict]:
        """
        Get list of failed/exited containers

        Args:
            work_dir: Working directory

        Returns:
            List of container info dicts with 'name', 'state', 'exit_code', 'status'
        """
        import json

        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "-a", "--format", "json"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

            if not result.stdout.strip():
                return []

            failed = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    container = json.loads(line)
                    state = container.get("State", "").lower()
                    service = container.get("Service", "")

                    if not service:
                        continue

                    # Check for exited/failed containers
                    if "exited" in state or "dead" in state or "error" in state:
                        failed.append(
                            {
                                "name": service,
                                "state": container.get("State", ""),
                                "exit_code": container.get("ExitCode", "?"),
                                "status": container.get("Status", ""),
                            }
                        )
                except json.JSONDecodeError:
                    continue

            return failed
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ) as e:
            logger.warning(f"Failed to get failed containers: {e}")
            return []
