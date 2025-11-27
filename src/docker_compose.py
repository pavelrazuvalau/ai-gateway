"""
Docker Compose override file generation
"""

from typing import List, Dict, Optional, Any, Union
from .config import ResourceProfile
from .utils import print_success, set_file_permissions


# Worker recommendations and web search profiles
# See docs/system-requirements.md for detailed memory usage metrics and resource profiles
WEB_SEARCH_PROFILES = {
    ResourceProfile.SMALL_VPS: {
        # See docs/system-requirements.md#small-vps-2gb-ram-2-cpu-cores for details
        "web_search_concurrent_requests": 1,
        "web_search_result_count": 1,
    },
    ResourceProfile.MEDIUM_VPS: {
        # See docs/system-requirements.md#medium-vps-4gb-ram-4-cpu-cores for details
        # Note: Web search limited to prevent CPU blocking (one request can use 80%+ CPU)
        "web_search_concurrent_requests": 1,
        "web_search_result_count": 1,
    },
    ResourceProfile.LARGE_VPS: {
        # See docs/system-requirements.md#large-vps-8gb-ram-8-cpu-cores for details
        "web_search_concurrent_requests": 2,
        "web_search_result_count": 3,
    },
    ResourceProfile.DESKTOP: {
        # Desktop: ample resources, but still optimized for multi-user scenarios
        "web_search_concurrent_requests": 3,
        "web_search_result_count": 4,
    },
}

PROFILE_TEMPLATES = {
    ResourceProfile.DESKTOP: {
        "postgres": {},
        "litellm": {
            # Desktop profile: 4 workers for unlimited resources
            # See docs/system-requirements.md for memory usage details
            "num_workers": 4,
        },
        "open_webui": {},
    },
    ResourceProfile.SMALL_VPS: {
        "postgres": {},
        "litellm": {
            # Small VPS: 1 worker (2GB RAM is tight, actual usage ~2.3-2.5GB)
            # See docs/system-requirements.md#small-vps-2gb-ram-2-cpu-cores for details
            # Consider lightweight Linux distro or upgrade to Medium VPS (4GB)
            "num_workers": 1,
        },
        "open_webui": {},
    },
    ResourceProfile.MEDIUM_VPS: {
        "postgres": {},
        "litellm": {
            # Medium VPS: 2 workers (uses ~3.3GB, leaves ~700MB buffer)
            # See docs/system-requirements.md#medium-vps-4gb-ram-4-cpu-cores for details
            "num_workers": 2,
        },
        "open_webui": {},
    },
    ResourceProfile.LARGE_VPS: {
        "postgres": {},
        "litellm": {
            # Large VPS: 6 workers (uses ~5.1GB, leaves ~3GB buffer for 8GB system)
            # See docs/system-requirements.md#large-vps-8gb-ram-8-cpu-cores for details
            "num_workers": 6,
        },
        "open_webui": {},
    },
}


def generate_docker_compose_override(
    profile: Optional[ResourceProfile],
    port_config: Dict[str, Any],
    selected_models: List[str],
) -> None:
    """
    Generate docker-compose.override.yml file
    """
    try:
        import yaml
    except ImportError:
        # Fallback: if yaml is not available, show error
        print("ERROR: PyYAML is not installed. Install: pip install pyyaml")
        raise ImportError("PyYAML required for docker-compose.override.yml generation")
    
    # Models are configured via Admin UI, no need to list them here
    default_models_str = "Configured via Admin UI"
    
    # Get profile template (if profile is None, use empty template - no workers config)
    if profile is not None:
        template = PROFILE_TEMPLATES.get(profile, PROFILE_TEMPLATES[ResourceProfile.MEDIUM_VPS])
    else:
        template = {"postgres": {}, "litellm": {}, "open_webui": {}}
    
    # Build override structure
    override = {
        "services": {}
    }
    
    # PostgreSQL
    # No optimizations needed - using defaults like official config
    
    # LiteLLM
    # Use configured port from port_config
    litellm_internal_port = port_config.get("litellm_internal_port", 4000)
    
    # Get num_workers from profile template (see docs/system-requirements.md for worker calculations)
    if profile is not None and "litellm" in template and "num_workers" in template["litellm"]:
        num_workers = str(template["litellm"]["num_workers"])
        # Override command to set workers and port
        override["services"]["litellm"] = {
            "command": f"--config /app/config.yaml --host 0.0.0.0 --port {litellm_internal_port} --num_workers {num_workers} --detailed_debug",
        }
    elif litellm_internal_port != 4000:
        # Only override command if port is not standard
        override["services"]["litellm"] = {
            "command": f"--config /app/config.yaml --host 0.0.0.0 --port {litellm_internal_port} --detailed_debug",
        }
    
    # Always set DEBUG log level for diagnostics
    # Initialize litellm service if not already created
    if "litellm" not in override["services"]:
        override["services"]["litellm"] = {}
    if "environment" not in override["services"]["litellm"]:
        override["services"]["litellm"]["environment"] = []
    override["services"]["litellm"]["environment"].append("LITELLM_LOG_LEVEL=DEBUG")
    override["services"]["litellm"]["environment"].append("SET_VERBOSE=True")
    override["services"]["litellm"]["environment"].append(
        "DATABASE_URL=postgresql://${POSTGRES_USER:-litellm}:${POSTGRES_PASSWORD:-litellm_password}@postgres:5432/${POSTGRES_DB:-litellm}"
    )
    # Add PYTHONPATH to find custom callbacks
    override["services"]["litellm"]["environment"].append("PYTHONPATH=/app:/app/litellm_callbacks")
    
    # Mount custom callbacks directory for tool call validation
    if "volumes" not in override["services"]["litellm"]:
        override["services"]["litellm"]["volumes"] = []
    override["services"]["litellm"]["volumes"].append("./litellm_callbacks:/app/litellm_callbacks:ro")
    
    # Ports configuration
    if port_config.get("use_nginx"):
        override["services"]["litellm"]["ports"] = []
    else:
        override["services"]["litellm"]["ports"] = [
            f"{port_config.get('litellm_external_port')}:{litellm_internal_port}"
        ]
        
    
    # Open WebUI
    # Get Web Search configuration based on resource profile
    # Defaults to Medium VPS if profile is None or not found
    if profile is not None and profile in WEB_SEARCH_PROFILES:
        web_search_config = WEB_SEARCH_PROFILES[profile]
    else:
        # Default to Medium VPS settings if profile is None
        web_search_config = WEB_SEARCH_PROFILES[ResourceProfile.MEDIUM_VPS]
    
    override["services"]["open-webui"] = {
        "environment": [
            f"DEFAULT_MODELS={default_models_str}",
            # Web search config (profile-optimized, see docs/configuration.md)
            "BYPASS_WEB_SEARCH_WEB_LOADER=${BYPASS_WEB_SEARCH_WEB_LOADER:-true}",
            "WEB_SEARCH_ENGINE=${WEB_SEARCH_ENGINE:-tavily}",
            f"WEB_SEARCH_CONCURRENT_REQUESTS=${{WEB_SEARCH_CONCURRENT_REQUESTS:-{web_search_config['web_search_concurrent_requests']}}}",
            f"WEB_SEARCH_RESULT_COUNT=${{WEB_SEARCH_RESULT_COUNT:-{web_search_config['web_search_result_count']}}}",
            # Tavily API Key (required if WEB_SEARCH_ENGINE=tavily)
            "TAVILY_API_KEY=${TAVILY_API_KEY:-}",
        ],
    }
    
    # Open WebUI connects directly to LiteLLM (see docs/configuration.md for architecture)
    if port_config.get("use_nginx"):
        # Open WebUI connects directly to LiteLLM (inside Docker network)
        litellm_internal_port = port_config.get('litellm_internal_port', 4000)
        override["services"]["open-webui"]["environment"].extend([
            f"OPENAI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            f"WEBUI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            # Virtual Key preferred over Master Key (see docs/configuration/virtual-key.md)
            "OPENAI_API_KEY=${VIRTUAL_KEY:-${LITELLM_MASTER_KEY}}",
        ])
    else:
        # Without nginx - direct connection to LiteLLM container
        litellm_internal_port = port_config.get('litellm_internal_port', 4000)
        override["services"]["open-webui"]["environment"].extend([
            f"OPENAI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            f"WEBUI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            # Virtual Key preferred over Master Key (see docs/configuration/virtual-key.md)
            "OPENAI_API_KEY=${VIRTUAL_KEY:-${LITELLM_MASTER_KEY}}",
        ])
    
    # Ports for Open WebUI
    # For nginx: services on internal ports, nginx proxies to them
    # Without nginx: services on external ports
    if port_config.get("use_nginx"):
        # Nginx proxies to internal ports
        # Ports are not exposed externally, only within Docker network
        override["services"]["open-webui"]["ports"] = []
    else:
        # Without nginx - ports are exposed externally
        webui_internal_port = port_config.get('webui_internal_port', 8080)
        override["services"]["open-webui"]["ports"] = [
            f"{port_config.get('webui_external_port')}:{webui_internal_port}"
        ]
    
    # Deploy resources for open-webui (only if not False)
    if "open_webui" in template and "deploy" in template["open_webui"]:
        deploy_config = template["open_webui"]["deploy"]
        if deploy_config is not False:
            override["services"]["open-webui"]["deploy"] = {
                "resources": deploy_config
            }
    
    # LiteLLM ports (see docs/configuration.md for port configuration details)
    if port_config.get("use_nginx"):
        # Map external port for LiteLLM UI
        litellm_external_port = port_config.get('litellm_external_port')
        if litellm_external_port:
            litellm_internal_port = port_config.get('litellm_internal_port', 4000)
            if "litellm" not in override["services"]:
                override["services"]["litellm"] = {}
            override["services"]["litellm"]["ports"] = [
                f"{litellm_external_port}:{litellm_internal_port}"
            ]
    else:
        # Without nginx - LiteLLM exposed on external port
        litellm_external_port = port_config.get('litellm_external_port')
        if litellm_external_port:
            litellm_internal_port = port_config.get('litellm_internal_port', 4000)
            if "litellm" not in override["services"]:
                override["services"]["litellm"] = {}
            override["services"]["litellm"]["ports"] = [
                f"{litellm_external_port}:{litellm_internal_port}"
            ]
    
    # Nginx
    if port_config.get("use_nginx"):
        override["services"]["nginx"] = {"ports": []}
        nginx_ports = []
        
        # Use nginx_http_port from port_config (HTTP only, see docs/nginx/README.md for SSL)
        nginx_http_port = port_config.get('nginx_http_port')
        if not nginx_http_port:
            # Fallback: should not happen, but safety check
            nginx_http_port = port_config.get('nginx_port', '80')
        nginx_ports.append(f"{nginx_http_port}:80")
        
        override["services"]["nginx"]["ports"] = nginx_ports
    
    # Write YAML file
    try:
        with open("docker-compose.override.yml", "w", encoding="utf-8") as f:
            f.write("# docker-compose.override.yml\n")
            f.write("# Auto-generated by setup.py\n")
            f.write(f"# Resource profile: {profile.value}\n")
            f.write(f"# Nginx: {'yes' if port_config.get('use_nginx') else 'no'}\n")
            f.write("# This file contains user settings and should NOT be committed to git\n")
            f.write("# Docker Compose automatically applies it on top of docker-compose.yml\n\n")
            yaml.dump(override, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except (IOError, OSError, PermissionError, yaml.YAMLError) as e:
        from .utils import print_error
        print_error(f"Error writing docker-compose.override.yml file: {e}")
        raise RuntimeError(f"Failed to create docker-compose.override.yml file: {e}") from e
    
    set_file_permissions("docker-compose.override.yml", 0o600)
    print_success("docker-compose.override.yml created")
    print_success("Permissions set: 600 (owner only)")

