"""
Systemd service installation and management
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple
from ..infrastructure.logger import get_logger

logger = get_logger(__name__)


class SystemdService:
    """Manages systemd user service for AI Gateway"""
    
    SERVICE_NAME = "ai-gateway.service"
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.service_dir = Path.home() / ".config" / "systemd" / "user"
        self.service_file = self.service_dir / self.SERVICE_NAME
    
    def _run_command(self, cmd: list, check: bool = True) -> Tuple[int, str, str]:
        """Run shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except Exception as e:
            return 1, "", str(e)
    
    def is_installed(self) -> bool:
        """Check if service is installed"""
        return self.service_file.exists()
    
    def is_enabled(self) -> bool:
        """Check if service is enabled"""
        code, out, _ = self._run_command(
            ["systemctl", "--user", "is-enabled", self.SERVICE_NAME],
            check=False
        )
        return code == 0 and "enabled" in out
    
    def is_active(self) -> bool:
        """Check if service is active"""
        code, out, _ = self._run_command(
            ["systemctl", "--user", "is-active", self.SERVICE_NAME],
            check=False
        )
        return code == 0 and "active" in out
    
    def is_lingering_enabled(self) -> bool:
        """Check if lingering is enabled for current user"""
        import os
        username = os.getenv('USER') or os.getenv('USERNAME')
        if not username:
            return False
        code, out, _ = self._run_command(
            ["loginctl", "show-user", username],
            check=False
        )
        return "Linger=yes" in out
    
    def _generate_service_content(self) -> str:
        """Generate systemd service file content"""
        return f"""[Unit]
Description=AI Gateway - LiteLLM, Open WebUI, PostgreSQL, Nginx
Documentation=https://github.com/pavelrazuvalau/ai-gateway
After=docker.service
Wants=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory={self.project_root}

# Environment
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

# Start command (docker compose up -d)
# Note: don't use -f flag to let docker compose automatically find both
# docker-compose.yml and docker-compose.override.yml
ExecStart=/usr/bin/docker compose up -d --remove-orphans

# Stop command (docker compose down)
ExecStop=/usr/bin/docker compose down

# Restart policy
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-gateway

[Install]
WantedBy=default.target
"""
    
    def install(self) -> bool:
        """Install systemd service"""
        try:
            # Create service directory
            self.service_dir.mkdir(parents=True, exist_ok=True)
            
            # Write service file
            content = self._generate_service_content()
            self.service_file.write_text(content)
            logger.info(f"Created service file: {self.service_file}")
            
            # Reload systemd
            code, _, err = self._run_command(
                ["systemctl", "--user", "daemon-reload"]
            )
            if code != 0:
                logger.error(f"Failed to reload systemd: {err}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to install service: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable service autostart"""
        try:
            code, _, err = self._run_command(
                ["systemctl", "--user", "enable", self.SERVICE_NAME]
            )
            if code != 0:
                logger.error(f"Failed to enable service: {err}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to enable service: {e}")
            return False
    
    def enable_lingering(self) -> bool:
        """Enable lingering for current user (allows services to run after logout)"""
        try:
            import os
            username = os.getenv('USER') or os.getenv('USERNAME')
            if not username:
                logger.warning("Could not determine username")
                return False
            
            code, _, err = self._run_command(
                ["loginctl", "enable-linger", username]
            )
            if code != 0:
                logger.warning(f"Failed to enable lingering: {err}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Failed to enable lingering: {e}")
            return False
    
    def start(self) -> bool:
        """Start the service"""
        try:
            code, _, err = self._run_command(
                ["systemctl", "--user", "start", self.SERVICE_NAME]
            )
            if code != 0:
                logger.error(f"Failed to start service: {err}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the service"""
        try:
            code, _, err = self._run_command(
                ["systemctl", "--user", "stop", self.SERVICE_NAME]
            )
            if code != 0:
                logger.error(f"Failed to stop service: {err}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to stop service: {e}")
            return False
    
    def status(self) -> Tuple[bool, str]:
        """Get service status"""
        try:
            code, out, _ = self._run_command(
                ["systemctl", "--user", "status", self.SERVICE_NAME],
                check=False
            )
            return code == 0, out
        except Exception as e:
            return False, str(e)
    
    def uninstall(self) -> bool:
        """Uninstall systemd service"""
        try:
            # Stop service if running
            self.stop()
            
            # Disable service
            self._run_command(
                ["systemctl", "--user", "disable", self.SERVICE_NAME],
                check=False
            )
            
            # Remove service file
            if self.service_file.exists():
                self.service_file.unlink()
            
            # Reload systemd
            self._run_command(
                ["systemctl", "--user", "daemon-reload"]
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to uninstall service: {e}")
            return False

