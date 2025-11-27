"""
OpenWebUI database utilities for updating web search settings from environment variables.

See docs/configuration.md#web-search-configuration for web search configuration details.
"""

import sqlite3
from typing import Optional, Dict
from ..infrastructure.logger import get_logger

logger = get_logger(__name__)


def update_web_search_settings_from_env(container_name: str = "open-webui", env_vars: Optional[Dict[str, str]] = None) -> bool:
    """
    Update web search settings in OpenWebUI database from environment variables
    
    OpenWebUI stores settings in config.data as JSON. This function:
    1. Reads environment variables from the container
    2. Updates the JSON config in the database to match env vars
    3. This ensures env vars take precedence over UI settings
    
    Args:
        container_name: Name of the OpenWebUI container
        env_vars: Optional dict of env vars to use (if None, reads from container)
        
    Returns:
        True if settings were updated successfully, False otherwise
    """
    try:
        import subprocess
        import json
        
        # Check if container is running
        result = subprocess.run(
            ["docker", "exec", container_name, "test", "-f", "/app/backend/data/webui.db"],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            # Database doesn't exist or container not running - nothing to update
            logger.debug("OpenWebUI database not found or container not running")
            return True
        
        # Get environment variables from container if not provided
        if env_vars is None:
            result = subprocess.run(
                ["docker", "exec", container_name, "env"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("Could not read environment variables from container")
                return False
            
            env_vars = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        
        # Map environment variables to OpenWebUI config paths
        # OpenWebUI stores settings in config.data as nested JSON
        env_to_config = {
            'WEB_SEARCH_ENGINE': 'rag.web.search.engine',
            'WEB_SEARCH_CONCURRENT_REQUESTS': 'rag.web.search.concurrent_requests',
            'WEB_SEARCH_RESULT_COUNT': 'rag.web.search.result_count',
            'BYPASS_WEB_SEARCH_WEB_LOADER': 'rag.web.search.bypass_web_loader',
        }
        
        # First, check if engine is already set in database
        # We need to read current config to preserve existing engine
        python_check_script = """
import sqlite3
import json
import sys

try:
    conn = sqlite3.connect('/app/backend/data/webui.db')
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM config WHERE id = 1')
    result = cursor.fetchone()
    
    if result:
        config = json.loads(result[0])
        search_engine = config.get('rag', {}).get('web', {}).get('search', {}).get('engine')
        if search_engine:
            print(f"EXISTING_ENGINE:{search_engine}")
        else:
            print("NO_ENGINE")
    else:
        print("NO_CONFIG")
    
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"ERROR:{str(e)}")
    sys.exit(1)
"""
        
        # Check existing engine
        check_result = subprocess.run(
            ["docker", "exec", container_name, "python3", "-c", python_check_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        existing_engine = None
        if check_result.returncode == 0:
            if "EXISTING_ENGINE:" in check_result.stdout:
                existing_engine = check_result.stdout.split("EXISTING_ENGINE:")[1].strip()
        
        # Build update script
        updates = {}
        for env_key, config_path in env_to_config.items():
            # Skip WEB_SEARCH_ENGINE if it's already set in database
            if env_key == 'WEB_SEARCH_ENGINE' and existing_engine:
                logger.debug(f"Preserving existing search engine: {existing_engine}")
                continue
            
            if env_key in env_vars and env_vars[env_key]:
                value = env_vars[env_key]
                lowered = value.lower()
                if lowered in ("true", "false"):
                    value = lowered == "true"
                else:
                    try:
                        if '.' not in value:
                            value = int(value)
                        else:
                            value = float(value)
                    except ValueError:
                        pass  # Keep as string
                updates[config_path] = value
        
        # If bypass_web_loader is True, also clear loader.engine to prevent Playwright usage
        if 'rag.web.search.bypass_web_loader' in updates and updates['rag.web.search.bypass_web_loader'] is True:
            updates['rag.web.loader.engine'] = None  # Clear playwright engine
        
        # Enable RAG if web search settings are being configured
        # This ensures web search works even if it was disabled by default in new OpenWebUI builds
        if updates:
            updates['rag.enabled'] = True
        
        if not updates:
            logger.debug("No web search environment variables found to update")
            return True
        
        # Python script to update config.data JSON
        python_script = f"""
import sqlite3
import json
import sys

try:
    conn = sqlite3.connect('/app/backend/data/webui.db')
    cursor = conn.cursor()
    
    # Get current config
    cursor.execute('SELECT data FROM config WHERE id = 1')
    result = cursor.fetchone()
    
    if not result:
        print("INFO: No config found in database")
        conn.close()
        sys.exit(0)
    
    # Parse JSON
    config = json.loads(result[0])
    
    # Update nested paths
    updates = {repr(updates)}
    updated = False
    
    for path, value in updates.items():
        keys = path.split('.')
        current = config
        # Navigate to the parent dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {{}}
            current = current[key]
        # Set the value (or delete if None)
        old_value = current.get(keys[-1])
        if value is None:
            # Remove key if value is None (e.g., to clear playwright engine)
            if keys[-1] in current:
                del current[keys[-1]]
                updated = True
        else:
            current[keys[-1]] = value
            if old_value != value:
                updated = True
    
    if updated:
        # Save updated config
        cursor.execute('UPDATE config SET data = ? WHERE id = 1', (json.dumps(config),))
        conn.commit()
        print("SUCCESS: Web search settings updated from environment variables")
    else:
        print("INFO: Settings already match environment variables")
    
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        
        # Execute Python script in container
        result = subprocess.run(
            ["docker", "exec", container_name, "python3", "-c", python_script],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            if "SUCCESS" in result.stdout:
                logger.info("Web search settings updated from environment variables")
                return True
            elif "INFO" in result.stdout:
                logger.debug(result.stdout.strip())
                return True
            else:
                logger.warning(f"Could not update web search settings: {result.stdout}")
                return False
        else:
            logger.warning(f"Failed to update web search settings: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning("Timeout while trying to update web search settings")
        return False
    except FileNotFoundError:
        logger.debug("Docker command not found")
        return False
    except Exception as e:
        logger.warning(f"Error updating web search settings: {e}")
        return False


def update_web_search_settings_on_start(container_name: str = "open-webui") -> bool:
    """
    Update web search settings when container starts (if UPDATE_WEB_SEARCH_SETTINGS flag is set)
    
    This function waits for the container to be running and database to be accessible,
    then updates settings from environment variables.
    
    Args:
        container_name: Name of the OpenWebUI container
        
    Returns:
        True if successful, False otherwise
    """
    import time
    import subprocess
    
    # Wait for container to be running (max 30 seconds)
    max_wait = 30
    wait_interval = 2
    waited = 0
    
    while waited < max_wait:
        try:
            # Check if container is running
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if container_name in result.stdout:
                # Container is running, try to update settings
                return update_web_search_settings_from_env(container_name)
            
            # Wait a bit before retrying
            time.sleep(wait_interval)
            waited += wait_interval
            
        except Exception as e:
            logger.debug(f"Error checking container status: {e}")
            time.sleep(wait_interval)
            waited += wait_interval
    
    logger.warning(f"Container {container_name} did not start within {max_wait} seconds")
    return False

