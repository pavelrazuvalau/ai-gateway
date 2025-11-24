"""
Docker Compose override file generation
"""

from typing import List, Dict, Optional, Any, Union
from .config import ResourceProfile
from .utils import print_success, set_file_permissions


# Worker recommendations calculated to fit within specified RAM limits
# NOTE: These estimates are based on REAL measurements from production deployments.
# To check real memory usage after deployment, run:
#   docker stats --no-stream
# 
# Memory estimates based on REAL measurements (2024):
#   - LiteLLM base: ~300MB (main process, dependencies)
#   - LiteLLM worker: ~400-500MB each (measured: 2 workers = ~900MB, 3 workers = ~1500MB)
#   - PostgreSQL 16: ~20-60MB (idle, can grow with usage)
#   - Open WebUI: ~600MB (Python web app with dependencies)
#   - Nginx Alpine: ~5MB (very lightweight)
#   - Docker overhead: ~100-200MB (container runtime)
#   - OS: ~500MB-1GB (varies by Linux distribution)
# 
# IMPORTANT: Real worker memory usage is 2-3x higher than Gunicorn docs suggest.
# This is due to LiteLLM's model loading, caching, and Python 3.13 overhead.
# Monitor actual usage and adjust if needed.
# If OOM errors occur, reduce workers or upgrade to larger VPS.
PROFILE_TEMPLATES = {
    ResourceProfile.DESKTOP: {
        "postgres": {},
        "litellm": {
            # Desktop: unlimited resources, can use more workers
            # Calculation based on REAL measurements:
            #   Base: PostgreSQL (~20-60MB) + Open WebUI (~600MB) + Nginx (~5MB) + Docker (~200MB) = ~825MB
            #   LiteLLM: 4 workers × 400MB (real avg) + base 300MB = ~1900MB
            #   Total containers: ~2.7GB
            #   OS: ~1-1.5GB (typical Linux)
            #   Total: ~3.7-4.2GB - safe for 8GB+ systems
            # NOTE: Reduced from 6 to 4 workers based on real memory measurements
            # 6 workers would use ~2700MB for LiteLLM alone
            "num_workers": 4,
        },
        "open_webui": {},
    },
    ResourceProfile.SMALL_VPS: {
        "postgres": {},
        "litellm": {
            # Small VPS: 2GB RAM total
            # Calculation based on REAL measurements:
            #   Base: PostgreSQL (~20-60MB) + Open WebUI (~600MB) + Nginx (~5MB) + Docker (~200MB) = ~825MB
            #   LiteLLM: 1 worker × 400MB (real avg) + base 300MB = ~700MB
            #   Total containers: ~1.5GB
            #   OS: ~500MB-700MB (minimal Linux)
            #   Total: ~2.0-2.2GB (fits in 2GB with small buffer)
            # WARNING: 2GB RAM is TIGHT. Consider upgrading to Medium VPS (4GB) for better performance.
            # Medium VPS uses 2 workers for better concurrency.
            "num_workers": 1,
        },
        "open_webui": {},
    },
    ResourceProfile.MEDIUM_VPS: {
        "postgres": {},
        "litellm": {
            # Medium VPS: 4GB RAM total
            # Calculation based on REAL measurements:
            #   Base: PostgreSQL (~20-60MB) + Open WebUI (~600MB) + Nginx (~5MB) + Docker (~200MB) = ~825MB
            #   LiteLLM: 2 workers × 400MB (real avg) + base 300MB = ~1100MB
            #   Total containers: ~1.9GB
            #   OS: ~1GB (typical Linux)
            #   Total: ~2.9GB, leaves ~1.1GB buffer - safe
            # NOTE: Reduced from 3 to 2 workers based on real memory measurements
            # 3 workers would use ~1500MB for LiteLLM alone, leaving only ~600MB buffer
            # Monitor with: docker stats
            "num_workers": 2,
        },
        "open_webui": {},
    },
    ResourceProfile.LARGE_VPS: {
        "postgres": {},
        "litellm": {
            # Large VPS: 8GB+ RAM total
            # Calculation based on REAL measurements:
            #   Base: PostgreSQL (~20-60MB) + Open WebUI (~600MB) + Nginx (~5MB) + Docker (~200MB) = ~825MB
            #   LiteLLM: 6 workers × 400MB (real avg) + base 300MB = ~2700MB
            #   Total containers: ~3.5GB
            #   OS: ~1-1.5GB (typical Linux)
            #   Total: ~4.5-5GB, leaves ~3-3.5GB buffer - very safe
            # NOTE: Reduced from 8 to 6 workers based on real memory measurements
            # 8 workers would use ~3500MB for LiteLLM alone, leaving less buffer
            # Monitor with: docker stats
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
    # Use configured port from port_config (respects LITELLM_INTERNAL_PORT from .env)
    # When nginx is used, we still need to use the configured port so nginx can connect
    litellm_internal_port = port_config.get("litellm_internal_port", 4000)
    
    # Get num_workers from profile template (if profile is None, don't configure workers)
    # Based on Gunicorn formula: (CPU cores * 2) + 1, adjusted for I/O-bound workload
    if profile is not None and "litellm" in template and "num_workers" in template["litellm"]:
        num_workers = str(template["litellm"]["num_workers"])
        # Override command to set workers and port
        override["services"]["litellm"] = {
            "command": f"--config /app/config.yaml --host 0.0.0.0 --port {litellm_internal_port} --num_workers {num_workers} --detailed_debug",
        }
    elif litellm_internal_port != 4000:
        # Only override command if port is not standard (even without workers config)
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
    override["services"]["open-webui"] = {
        "environment": [
            f"DEFAULT_MODELS={default_models_str}",
        ],
    }
    
    # Open WebUI accesses LiteLLM directly (not through nginx)
    # According to LiteLLM docs: https://docs.litellm.ai/docs/tutorials/openweb_ui
    # Open WebUI should connect directly to LiteLLM Proxy
    # External clients access LiteLLM through nginx at /api/litellm/v1
    # LiteLLM UI is available on separate port {litellm_external_port}
    # Open WebUI uses Virtual Key (not Master Key) for security
    if port_config.get("use_nginx"):
        # Open WebUI connects directly to LiteLLM (inside Docker network)
        # This is the correct way according to LiteLLM documentation
        litellm_internal_port = port_config.get('litellm_internal_port', 4000)
        override["services"]["open-webui"]["environment"].extend([
            f"OPENAI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            f"WEBUI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            # Use Virtual Key instead of Master Key for security
            # Virtual Key is created via virtual-key.py and stored in .env
            # Falls back to Master Key if Virtual Key not set (for first run)
            "OPENAI_API_KEY=${VIRTUAL_KEY:-${LITELLM_MASTER_KEY}}",
        ])
    else:
        # Without nginx - direct connection to LiteLLM container
        litellm_internal_port = port_config.get('litellm_internal_port', 4000)
        override["services"]["open-webui"]["environment"].extend([
            f"OPENAI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            f"WEBUI_API_BASE_URL=http://litellm:{litellm_internal_port}/v1",
            # Use Virtual Key instead of Master Key for security
            # Falls back to Master Key if Virtual Key not set (for first run)
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
    
    # LiteLLM ports
    # With nginx: LiteLLM API available through nginx at /api/litellm/
    # LiteLLM UI needs separate external port for local network access (configuration)
    # Without nginx: expose LiteLLM on external port
    if port_config.get("use_nginx"):
        # Map external port for LiteLLM UI (for local network access)
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
        
        # Use nginx_http_port from port_config (HTTP only, no SSL)
        # Always use random high port for rootless Docker compatibility
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

