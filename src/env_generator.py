"""
Environment file (.env) generation
DEPRECATED: Use infrastructure.security.SecurityService for password generation
"""

import os
from typing import List, Dict, Optional, Any
from pathlib import Path
from .utils import print_success, print_info, set_file_permissions, ensure_dir

# Try to use SecurityService, fallback to old implementation
try:
    from .infrastructure.security import SecurityService
    _USE_SECURITY_SERVICE = True
except ImportError:
    _USE_SECURITY_SERVICE = False
    import secrets
    import subprocess


def generate_master_key() -> str:
    """
    Generate LiteLLM master key
    DEPRECATED: Use SecurityService.generate_master_key() instead
    """
    if _USE_SECURITY_SERVICE:
        return SecurityService.generate_master_key()
    # Fallback to old implementation
    return f"sk-{secrets.token_urlsafe(32)}"


def generate_password(length: int = 32) -> str:
    """
    Generate secure random password
    DEPRECATED: Use SecurityService.generate_password() instead
    """
    if _USE_SECURITY_SERVICE:
        return SecurityService.generate_password(length)
    # Fallback to old implementation
    try:
        from .core.constants import SUBPROCESS_TIMEOUT
        result = subprocess.run(
            ["openssl", "rand", "-base64", str(length)],
            capture_output=True,
            text=True,
            check=True,
            timeout=SUBPROCESS_TIMEOUT
        )
        password = result.stdout.strip()
        password = password.replace("=", "").replace("+", "").replace("/", "")
        return password[:length]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return secrets.token_urlsafe(length)[:length]


def generate_env_file(
    master_key: str,
    ui_password: str,
    postgres_password: str,
    postgres_port: int,
    port_config: Dict[str, Any],
    webui_secret: str,
    ui_username: str = "admin",
    preserve_first_run: bool = False,
) -> None:
    """
    Generate .env file with all configuration
    
    Args:
        master_key: LiteLLM master key (should start with 'sk-')
        ui_password: UI password
        postgres_password: PostgreSQL password
        postgres_port: PostgreSQL port
        port_config: Port configuration dictionary
        webui_secret: WebUI secret key
        ui_username: UI username (default: 'admin')
    
    Raises:
        ValidationError: If input parameters are invalid
        FileOperationError: If file cannot be written
    """
    from .core.exceptions import ValidationError
    from .core.constants import MIN_PORT, MAX_PORT, DEFAULT_UI_USERNAME
    
    # Validation
    if not master_key or not master_key.startswith("sk-"):
        raise ValidationError("Master key must start with 'sk-'")
    if not ui_password or len(ui_password) < 8:
        raise ValidationError("UI password must be at least 8 characters")
    if not postgres_password or len(postgres_password) < 8:
        raise ValidationError("PostgreSQL password must be at least 8 characters")
    if not (MIN_PORT <= postgres_port <= MAX_PORT):
        raise ValidationError(f"PostgreSQL port must be between {MIN_PORT} and {MAX_PORT}")
    if not webui_secret or len(webui_secret) < 16:
        raise ValidationError("WebUI secret must be at least 16 characters")
    if not ui_username:
        ui_username = DEFAULT_UI_USERNAME
    env_content = []
    
    # Master key
    env_content.append("# LiteLLM Master Key (auto-generated)")
    env_content.append(f"LITELLM_MASTER_KEY={master_key}")
    env_content.append("")
    
    # UI credentials
    env_content.append("# LiteLLM Admin UI credentials (auto-generated)")
    env_content.append("# Dashboard access: http://localhost:4000/ui")
    env_content.append("# IMPORTANT: Use UI_USERNAME and UI_PASSWORD (without LITELLM_ prefix)")
    env_content.append(f"UI_USERNAME={ui_username}")
    env_content.append(f"UI_PASSWORD={ui_password}")
    env_content.append("")
    
    # PostgreSQL
    env_content.append("# PostgreSQL settings (password auto-generated)")
    env_content.append("POSTGRES_USER=litellm")
    env_content.append(f"POSTGRES_PASSWORD={postgres_password}")
    env_content.append("POSTGRES_DB=litellm")
    env_content.append(f"POSTGRES_PORT={postgres_port}")
    env_content.append("")
    
    # Internal ports
    env_content.append("# Internal ports (only for container-to-container communication)")
    env_content.append(f"LITELLM_INTERNAL_PORT={port_config['litellm_internal_port']}")
    env_content.append(f"WEBUI_INTERNAL_PORT={port_config['webui_internal_port']}")
    env_content.append("")
    
    # External ports
    # With nginx: LiteLLM API available through nginx
    # LiteLLM UI has separate external port for local network access (configuration)
    # Without nginx: both services have external ports
    if port_config.get('use_nginx'):
        env_content.append("# External ports (with nginx)")
        env_content.append(f"# LiteLLM API available through nginx at /api/litellm/")
        env_content.append(f"# LiteLLM UI has separate external port for local network access")
        litellm_ext_port = port_config.get('litellm_external_port', '')
        env_content.append(f"LITELLM_EXTERNAL_PORT={litellm_ext_port}")
        env_content.append("WEBUI_EXTERNAL_PORT=")
    else:
        env_content.append("# External ports (without nginx)")
        env_content.append(f"LITELLM_EXTERNAL_PORT={port_config.get('litellm_external_port', '')}")
        env_content.append(f"WEBUI_EXTERNAL_PORT={port_config.get('webui_external_port', '')}")
    env_content.append("")
    
    # Nginx settings
    env_content.append("# Nginx settings")
    env_content.append(f"USE_NGINX={'yes' if port_config.get('use_nginx') else 'no'}")
    # nginx_http_port should always be set (random high port for rootless Docker)
    nginx_http_port = port_config.get('nginx_http_port') or port_config.get('nginx_port', '')
    env_content.append(f"NGINX_HTTP_PORT={nginx_http_port}")
    env_content.append(f"NGINX_PORT={port_config.get('nginx_port', '')}")
    env_content.append("")
    
    # Budget profile
    budget_profile = port_config.get('budget_profile', 'test')
    env_content.append("# Budget profile (test/prod/unlimited)")
    env_content.append(f"BUDGET_PROFILE={budget_profile}")
    env_content.append("")
    
    # API keys
    env_content.append("# API keys for providers")
    env_content.append("# Configured through Admin UI: http://localhost:4000/ui")
    env_content.append("# Add required keys manually in .env or through Admin UI")
    env_content.append("")
    
    # WebUI secret
    env_content.append("# Open WebUI Secret Key (auto-generated)")
    env_content.append(f"WEBUI_SECRET_KEY={webui_secret}")
    env_content.append("")
    
    # First run flag (for showing setup instructions)
    # Only set to 'yes' if not preserving existing value
    if preserve_first_run:
        # Check if .env exists and has FIRST_RUN set
        env_file = Path(".env")
        existing_first_run = None
        existing_virtual_key = None
        if env_file.exists():
            try:
                from .utils import read_env_file
                existing_env = read_env_file(env_file)
                existing_first_run = existing_env.get("FIRST_RUN", "").strip()
                existing_virtual_key = existing_env.get("VIRTUAL_KEY", "").strip()
            except Exception:
                pass
        
        if existing_first_run:
            env_content.append("# First run flag (preserved from existing .env)")
            env_content.append(f"FIRST_RUN={existing_first_run}")
        else:
            env_content.append("# First run flag (set to 'no' after Virtual Key setup)")
            env_content.append("FIRST_RUN=yes")
        
        # Preserve Virtual Key if exists
        if existing_virtual_key:
            env_content.append("")
            env_content.append("# Virtual Key for Open WebUI (preserved from existing .env)")
            env_content.append(f"VIRTUAL_KEY={existing_virtual_key}")
    else:
        env_content.append("# First run flag (set to 'no' after Virtual Key setup)")
        env_content.append("FIRST_RUN=yes")
        env_content.append("")
        env_content.append("# Virtual Key for Open WebUI (REQUIRED - created via virtual-key.py)")
        env_content.append("# System will not start without Virtual Key")
        env_content.append("VIRTUAL_KEY=")
    env_content.append("")
    
    # Note: Models are configured through Admin UI: http://localhost:4000/ui
    
    # Write to file
    # Try to use FileRepository, fallback to direct file operations
    try:
        from .infrastructure.file_repository import FileRepository
        from .core.exceptions import FileOperationError
        
        repo = FileRepository(Path("."))
        repo.write_text(Path(".env"), "\n".join(env_content))
        repo.set_permissions(Path(".env"), 0o600)
    except (ImportError, AttributeError):
        # Fallback to old implementation
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write("\n".join(env_content))
        except (IOError, OSError, PermissionError) as e:
            from .utils import print_error
            from .core.exceptions import FileOperationError
            print_error(f"Error writing .env file: {e}")
            raise FileOperationError(f"Failed to create .env file: {e}") from e
        set_file_permissions(".env", 0o600)
    print_success(".env file created!")
    print_success("Permissions set: 600 (owner only)")
