"""
Script for creating LiteLLM Virtual Key and configuring Open WebUI.

This script helps with initial setup after first login to Open WebUI.

See docs/configuration/virtual-key.md for detailed information.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .utils import print_header, print_info, print_success, print_warning, print_error, Colors
from .utils import read_env_file


def create_virtual_key_via_api(
    litellm_url: str,
    master_key: str,
    team_name: str = "Open WebUI Team",
    key_name: str = "Open WebUI Key"
) -> Optional[str]:
    """
    Create a Virtual Key in LiteLLM via API.
    
    See docs/configuration/virtual-key.md#automatic-creation-recommended for details.
    
    Args:
        litellm_url: LiteLLM base URL (e.g., http://localhost:4000)
        master_key: LiteLLM Master Key
        team_name: Name for the team
        key_name: Name for the virtual key
        
    Returns:
        Virtual Key string or None if failed
    """
    try:
        # Try to create team and virtual key via LiteLLM API
        # LiteLLM API documentation: https://docs.litellm.ai/docs/proxy/virtual_keys
        
        print_info(f"Attempting to create Virtual Key via API...")
        print_info(f"LiteLLM URL: {litellm_url}")
        
        # Step 1: Create or get team
        team_data = {
            "team_alias": team_name,
            "team_id": team_name.lower().replace(" ", "-")
        }
        
        try:
            response = requests.post(
                f"{litellm_url}/team/new",
                json=team_data,
                headers={"Authorization": f"Bearer {master_key}"},
                timeout=10
            )
            if response.status_code in (200, 201):
                print_success(f"Team '{team_name}' created")
            elif response.status_code == 400:
                print_info(f"Team '{team_name}' may already exist")
            else:
                print_warning(f"Team creation returned status {response.status_code}")
        except Exception as e:
            print_warning(f"Cannot create team via API: {e}")
        
        # Step 2: Create virtual key
        key_data = {
            "team_id": team_name.lower().replace(" ", "-"),
            "key_alias": key_name,
            "models": [],  # Empty = access to all models
            "metadata": {"created_by": "virtual-key.py"}
        }
        
        try:
            response = requests.post(
                f"{litellm_url}/key/generate",
                json=key_data,
                headers={"Authorization": f"Bearer {master_key}"},
                timeout=10
            )
            if response.status_code in (200, 201):
                result = response.json()
                virtual_key = result.get("key", result.get("api_key"))
                if virtual_key:
                    print_success(f"Virtual Key created: {virtual_key[:20]}...")
                    return virtual_key
            elif response.status_code == 400:
                # Key might already exist, try to get existing keys
                error_msg = response.text
                if "already exists" in error_msg:
                    print_info("Virtual Key 'Open WebUI Key' already exists, trying to retrieve it...")
                    try:
                        list_response = requests.get(
                            f"{litellm_url}/key/list",
                            headers={"Authorization": f"Bearer {master_key}"},
                            timeout=10
                        )
                        if list_response.status_code == 200:
                            keys = list_response.json()
                            for key_info in keys.get("data", []):
                                if key_info.get("key_alias") == "Open WebUI Key":
                                    virtual_key = key_info.get("key")
                                    if virtual_key:
                                        print_success(f"Found existing Virtual Key: {virtual_key[:20]}...")
                                        return virtual_key
                    except Exception:
                        pass
                print_warning(f"Virtual Key creation returned status {response.status_code}")
                print_info(f"Response: {response.text[:200]}")
            else:
                print_warning(f"Virtual Key creation returned status {response.status_code}")
                print_info(f"Response: {response.text[:200]}")
        except Exception as e:
            print_warning(f"Cannot create Virtual Key via API: {e}")
        
        return None  # API creation failed, will use manual method
        
    except Exception as e:
        print_warning(f"Error creating Virtual Key via API: {e}")
        return None


def check_models_visibility(
    litellm_url: str,
    master_key: str
) -> Tuple[bool, int, int]:
    """
    Check if models exist and how many are public
    
    Args:
        litellm_url: LiteLLM base URL
        master_key: LiteLLM Master Key
        
    Returns:
        Tuple of (has_models, total_models, public_models_count)
    """
    try:
        # Get list of models
        response = requests.get(
            f"{litellm_url}/v1/models",
            headers={"Authorization": f"Bearer {master_key}"},
            timeout=10
        )
        
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get("data", [])
            
            if not models:
                return (False, 0, 0)
            
            # Check if any models are public
            public_models = [m for m in models if m.get("public", False)]
            
            return (True, len(models), len(public_models))
        else:
            return (False, 0, 0)
            
    except Exception:
        return (False, 0, 0)


def configure_openwebui_connection(
    virtual_key: str,
    litellm_url: str,
    use_nginx: bool = False,
    check_models: bool = True
) -> None:
    """
    Configure Open WebUI connection to LiteLLM.
    
    Note: Open WebUI configuration is typically done through UI.
    This function provides instructions.
    
    See docs/configuration/virtual-key.md#open-webui-configuration for details.
    
    Args:
        virtual_key: Virtual Key from LiteLLM
        litellm_url: LiteLLM base URL (for instructions)
        use_nginx: Whether Nginx is used (affects URL shown)
        check_models: Whether to check and suggest making models public
    """
    print_header("📝 Open WebUI Configuration")
    print()
    
    print_info("✅ Virtual Key is configured in Open WebUI environment")
    print_info("   Open WebUI will use this Virtual Key automatically for API requests")
    print()
    
    # Check models visibility if requested
    if check_models:
        env_vars = read_env_file(Path(".") / ".env")
        master_key = env_vars.get("LITELLM_MASTER_KEY", "").strip()
        
        if master_key:
            print_info("🔍 Checking models...")
            has_models, total_models, public_count = check_models_visibility(litellm_url, master_key)
            print()
            
            if not has_models:
                print_warning("⚠️  No models found in LiteLLM yet")
                print()
                print_info("📋 Next steps:")
                print_info("   1. Add models in LiteLLM UI:")
                print_info("      • Open LiteLLM UI: http://YOUR_IP:PORT/ui")
                print_info("      • Go to Models section")
                print_info("      • Add your models (Anthropic, OpenAI, etc.)")
                print()
                print_info("   2. After adding models, make them public:")
                print_info("      • In Models section, enable 'Public' for each model")
                print_info("      • Public models are visible to all Open WebUI users")
                print_info("      • Note: Public models still require API key (Virtual Key)")
                print_info("      • 'Public' only means 'visible to all users', not 'no auth required'")
                print()
            elif public_count == total_models:
                print_success(f"✅ All {total_models} model(s) are public")
                print_info("   All Open WebUI users will see these models")
                print()
            elif public_count > 0:
                print_warning(f"⚠️  Only {public_count}/{total_models} models are public")
                print()
                print_info("📋 To make all models visible to users:")
                print_info("   1. Open LiteLLM UI: http://YOUR_IP:PORT/ui")
                print_info("   2. Go to Models section")
                print_info("   3. Enable 'Public' for each model")
                print_info("   4. Public models are visible to all Open WebUI users")
                print_info("   5. Note: Public models still require API key (Virtual Key)")
                print()
            else:
                print_warning(f"⚠️  None of {total_models} models are public")
                print()
                print_info("📋 To make models visible to all users:")
                print_info("   1. Open LiteLLM UI: http://YOUR_IP:PORT/ui")
                print_info("   2. Go to Models section")
                print_info("   3. Enable 'Public' for each model")
                print_info("   4. Public models are visible to all Open WebUI users")
                print_info("   5. Note: Public models still require API key (Virtual Key)")
                print()
                print_info("💡 Alternative: Create separate Virtual Key per team/user")
                print_info("   • LiteLLM UI -> Teams -> create Team")
                print_info("   • Create Virtual Key for team with specific models")
                print_info("   • Open WebUI -> Settings -> Connections")
                print_info("   • Add connection with team's Virtual Key")
                print()
    
    print_success("✅ Virtual Key setup complete!")
    print()


def run_inside_docker_container(project_root: Path, master_key: str) -> Optional[str]:
    """
    Try to run Virtual Key creation inside Docker container.
    
    This avoids port issues by using Docker network directly.
    
    See docs/configuration/virtual-key.md#automatic-creation-recommended for details.
    
    Args:
        project_root: Project root directory
        master_key: LiteLLM Master Key
        
    Returns:
        Virtual Key string or None if failed
    """
    import subprocess
    
    try:
        print_info("Attempting to run setup inside Docker container...")
        print_info("This uses Docker network directly (avoids port issues)")
        print()
        
        # Check if litellm container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=litellm-proxy", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if not result.stdout.strip():
            print_warning("LiteLLM container is not running")
            return None
        
        container_name = result.stdout.strip()
        print_info(f"Found container: {container_name}")
        
        # Create a temporary script to run inside container
        # We'll use Python one-liner to create Virtual Key
        script_content = f"""
import sys
import requests
import json

master_key = "{master_key}"
litellm_url = "http://localhost:4000"

# Create team
team_data = {{"team_alias": "Open WebUI Team", "team_id": "open-webui-team"}}
try:
    response = requests.post(
        f"{{litellm_url}}/team/new",
        json=team_data,
        headers={{"Authorization": f"Bearer {{master_key}}"}},
        timeout=10
    )
except:
    pass

# Create virtual key
key_data = {{
    "team_id": "open-webui-team",
    "key_alias": "Open WebUI Key",
    "models": [],
    "metadata": {{"created_by": "virtual-key.py"}}
}}

try:
    response = requests.post(
        f"{{litellm_url}}/key/generate",
        json=key_data,
        headers={{"Authorization": f"Bearer {{master_key}}"}},
        timeout=10
    )
    if response.status_code in (200, 201):
        result = response.json()
        virtual_key = result.get("key", result.get("api_key"))
        if virtual_key:
            print(virtual_key)
            sys.exit(0)
    elif response.status_code == 400:
        # Key might already exist, try to get existing keys
        try:
            list_response = requests.get(
                f"{{litellm_url}}/key/list",
                headers={{"Authorization": f"Bearer {{master_key}}"}},
                timeout=10
            )
            if list_response.status_code == 200:
                keys = list_response.json()
                for key_info in keys.get("data", []):
                    if key_info.get("key_alias") == "Open WebUI Key":
                        virtual_key = key_info.get("key")
                        if virtual_key:
                            print(virtual_key)
                            sys.exit(0)
        except:
            pass
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        
        # Run Python script inside container
        result = subprocess.run(
            ["docker", "exec", container_name, "python3", "-c", script_content],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            virtual_key = result.stdout.strip()
            print_success(f"Virtual Key created via Docker: {virtual_key[:20]}...")
            return virtual_key
        else:
            print_warning(f"Docker execution failed: {result.stderr}")
            return None
            
    except Exception as e:
        print_warning(f"Cannot run inside Docker container: {e}")
        return None


def setup_virtual_key_interactive() -> Optional[str]:
    """
    Interactive setup for Virtual Key creation and Open WebUI configuration.
    
    See docs/configuration/virtual-key.md#automatic-creation-recommended for details.
    """
    print_header("🔑 LiteLLM Virtual Key Setup")
    print()
    print_info("This script helps you set up Virtual Key for Open WebUI")
    print_info("Virtual Key is more secure than Master Key for Open WebUI")
    print_info("It allows you to restrict access to specific models")
    print()
    
    # Load configuration
    project_root = Path(".")
    env_vars = read_env_file(project_root / ".env")
    
    master_key = env_vars.get("LITELLM_MASTER_KEY", "").strip()
    if not master_key:
        print_error("LITELLM_MASTER_KEY not found in .env")
        print_info("Run setup.sh first to generate configuration")
        return
    
    # Get LiteLLM URL for API access (needed for manual instructions and fallback)
    # Script runs on host, so we need external URL
    use_nginx = env_vars.get("USE_NGINX", "no").lower() in ("yes", "true", "1")
    if use_nginx:
        # With nginx, use LiteLLM external port for direct API access
        # (Nginx is for proxying, but we need direct LiteLLM API for Virtual Key creation)
        litellm_external_port = env_vars.get("LITELLM_EXTERNAL_PORT", "").strip()
        if not litellm_external_port:
            litellm_external_port = "4000"  # Fallback
        litellm_url = f"http://localhost:{litellm_external_port}"
    else:
        litellm_external_port = env_vars.get("LITELLM_EXTERNAL_PORT", "4000")
        litellm_url = f"http://localhost:{litellm_external_port}"
    
    # Try to run inside Docker container first (avoids port issues)
    virtual_key = run_inside_docker_container(project_root, master_key)
    
    if not virtual_key:
        # Fallback to host-based approach
        print()
        print_info("Using host-based approach (requires external port access)")
        print()
        print_info(f"Using LiteLLM URL: {litellm_url}")
        if use_nginx:
            print_info("Note: Open WebUI will use Docker network URL (http://litellm:4000) internally")
        
        print()
        
        # Check if LiteLLM is accessible
        try:
            response = requests.get(
                f"{litellm_url}/health",
                timeout=5,
                headers={"Authorization": f"Bearer {master_key}"}
            )
            if response.status_code == 200:
                print_success("LiteLLM is accessible")
            else:
                print_warning(f"LiteLLM returned status {response.status_code}")
                print_info("This is OK - Virtual Key creation may still work")
        except Exception as e:
            print_warning(f"Cannot connect to LiteLLM at {litellm_url}")
            print_info("This might be OK if LiteLLM is starting up")
            print_info("Make sure LiteLLM is running: docker compose ps")
            print()
            # Don't return - continue with setup, user can create Virtual Key manually
        
        # Try to create Virtual Key via API from host
        virtual_key = create_virtual_key_via_api(
            litellm_url=litellm_url,
            master_key=master_key
        )
    
    if not virtual_key:
        # Manual setup instructions
        print()
        print_warning("Virtual Key creation via API failed or not supported")
        print_error("Virtual Key is REQUIRED - system cannot start without it")
        print()
        print_info("Please create Virtual Key manually in LiteLLM UI:")
        print()
        print_info(f"1. Open LiteLLM UI: {litellm_url}/ui")
        print_info("2. Login with your credentials")
        print_info("3. Go to Teams/Users section")
        print_info("4. Create a Team (or use existing)")
        print_info("5. Create a Virtual Key for the team")
        print_info("6. Copy the Virtual Key")
        print()
        print_warning("⚠️  Virtual Key is required - cannot proceed without it")
        print_info("Enter Virtual Key (required):")
        while True:
            virtual_key = input("Virtual Key: ").strip()
            if virtual_key:
                if virtual_key.startswith("sk-"):
                    break
                else:
                    print_warning("Virtual Key should start with 'sk-'")
                    print_info("Please enter a valid Virtual Key:")
            else:
                print_error("Virtual Key is required - cannot skip")
                print_info("Please enter Virtual Key:")
    
    if virtual_key:
        print()
        configure_openwebui_connection(virtual_key, litellm_url, use_nginx=use_nginx, check_models=True)
        print()
        print_success("✅ Virtual Key setup complete!")
        print_info("Open WebUI will use Virtual Key for all API requests")
        print_info("This is more secure than using Master Key")
    # Virtual Key is now required - this should not happen
    if not virtual_key:
        print_error("❌ Virtual Key is required but was not provided")
        print_error("System cannot start without Virtual Key")
        return None
    
    return virtual_key


def main() -> int:
    """
    Main entry point for Virtual Key setup
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        virtual_key = setup_virtual_key_interactive()
        
        # Mark first run as complete and save Virtual Key
        project_root = Path(".")
        env_vars = read_env_file(project_root / ".env")
        if env_vars.get("FIRST_RUN", "no").lower() in ("yes", "true", "1") or virtual_key:
            # Update .env to mark first run as complete and store Virtual Key
            env_file = project_root / ".env"
            if env_file.exists():
                content = env_file.read_text(encoding="utf-8")
                # Replace FIRST_RUN=yes with FIRST_RUN=no
                content = content.replace("FIRST_RUN=yes", "FIRST_RUN=no")
                
                # Store Virtual Key in .env for display in start output
                if virtual_key:
                    # Remove old VIRTUAL_KEY if exists
                    lines = content.split('\n')
                    new_lines = []
                    skip_next = False
                    for i, line in enumerate(lines):
                        if skip_next:
                            skip_next = False
                            continue
                        if line.startswith("VIRTUAL_KEY=") or line.strip().startswith("# Virtual Key for Open WebUI"):
                            continue
                        new_lines.append(line)
                    
                    # Add Virtual Key after FIRST_RUN or at the end
                    added = False
                    for i, line in enumerate(new_lines):
                        if line.startswith("FIRST_RUN="):
                            new_lines.insert(i + 1, "")
                            new_lines.insert(i + 2, "# Virtual Key for Open WebUI (created via virtual-key.sh/virtual-key.bat)")
                            new_lines.insert(i + 3, f"VIRTUAL_KEY={virtual_key}")
                            added = True
                            break
                    
                    if not added:
                        # If FIRST_RUN not found, append at end
                        new_lines.append("")
                        new_lines.append("# Virtual Key for Open WebUI (created via virtual-key.sh/virtual-key.bat)")
                        new_lines.append(f"VIRTUAL_KEY={virtual_key}")
                    
                    content = '\n'.join(new_lines)
                    env_file.write_text(content, encoding="utf-8")
                    print()
                    print_success("✅ Virtual Key saved to .env")
                else:
                    # Just update FIRST_RUN
                    env_file.write_text(content, encoding="utf-8")
                    print()
                    print_success("✅ First run flag updated")
        
        return 0
    except KeyboardInterrupt:
        print()
        print_warning("Setup cancelled")
        return 1
    except Exception as e:
        print_error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

