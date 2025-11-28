"""
Continue.dev configuration service.

Generates optimized Continue.dev configuration from LiteLLM API.

See docs/integrations/continue-dev.md for detailed information.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

import requests

from ..infrastructure.file_repository import FileRepository
from ..infrastructure.logger import get_logger
from ..infrastructure.output import (
    Colors,
    ask_yes_no,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)

logger = get_logger(__name__)


class ContinueDevService:
    """
    Service for generating Continue.dev configuration.

    See docs/integrations/continue-dev.md for details.
    """

    def __init__(self, project_root: Path):
        """
        Initialize Continue.dev service

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.file_repo = FileRepository(self.project_root)
        self.output_config_file = (
            self.project_root / "continue-dev-config-generated.yaml"
        )
        self.output_prompts_dir = self.project_root / ".continue" / "prompts"
        self.output_system_prompt = self.output_prompts_dir / "system-prompt.md"

    def fetch_models_from_litellm(self, api_base: str, api_key: str) -> List[str]:
        """
        Fetch models from LiteLLM API using Virtual Key

        Args:
            api_base: LiteLLM API base URL
            api_key: Virtual Key for API access

        Returns:
            List of model IDs
        """
        # Normalize API base URL
        base_url = api_base.rstrip("/")

        # Determine models endpoint URL
        if "/api/litellm/v1" in base_url:
            models_url = f"{base_url}/models"
        elif base_url.endswith("/v1"):
            models_url = f"{base_url}/models"
        else:
            models_url = f"{base_url}/v1/models"

        try:
            response = requests.get(
                models_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                model_ids = [m.get("id", "") for m in models if m.get("id")]
                return model_ids
            else:
                logger.warning(f"Failed to fetch models: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.warning(f"Error fetching models: {e}")
            return []

    def check_models_available(self, api_base: str, api_key: str) -> Tuple[bool, int]:
        """
        Check if models are available via Virtual Key

        Args:
            api_base: LiteLLM API base URL
            api_key: Virtual Key for API access

        Returns:
            Tuple of (has_models, model_count)
        """
        models = self.fetch_models_from_litellm(api_base, api_key)
        return (len(models) > 0, len(models))

    def mask_api_key(self, api_key: str) -> str:
        """
        Safely mask API key for display

        Args:
            api_key: API key to mask

        Returns:
            Masked API key string
        """
        if not api_key:
            return "***"

        key_len = len(api_key)

        if key_len > 12:
            return f"{api_key[:8]}...{api_key[-4:]}"
        elif key_len >= 6:
            return f"{api_key[:4]}...{api_key[-2:]}"
        elif key_len >= 2:
            return f"{api_key[0]}...{api_key[-1]}"
        else:
            return "*" * min(key_len, 3)

    def get_api_config_from_env(self) -> Tuple[Optional[str], Optional[str], bool]:
        """
        Get API configuration from .env file

        Returns:
            Tuple of (api_base, virtual_key, use_nginx)
        """
        env_vars = self.file_repo.read_env_file(Path(".env"))

        use_nginx = env_vars.get("USE_NGINX", "no").lower() in ("yes", "true", "1")
        virtual_key = env_vars.get("VIRTUAL_KEY", "").strip()

        # Determine API base URL
        if use_nginx:
            nginx_port = (
                env_vars.get("NGINX_HTTP_PORT", "").strip()
                or env_vars.get("NGINX_PORT", "").strip()
            )
            if nginx_port:
                api_base = f"http://localhost:{nginx_port}/api/litellm/v1"
            else:
                api_base = None
        else:
            litellm_port = env_vars.get("LITELLM_EXTERNAL_PORT", "4000").strip()
            api_base = f"http://localhost:{litellm_port}/v1"

        return api_base, virtual_key, use_nginx

    def generate_model_name(self, model_id: str) -> str:
        """Generate human-readable model name from model ID"""
        model_lower = model_id.lower()

        # GPT models: "gpt-5-mini" -> "GPT-5 Mini"
        if model_lower.startswith("gpt-"):
            result = model_id.replace("gpt-", "GPT-", 1)
            result = re.sub(r"-([a-z])", lambda m: f" {m.group(1).upper()}", result)
        # Claude models: "claude-haiku-4-5" -> "Claude Haiku 4.5"
        elif model_lower.startswith("claude-"):
            result = re.sub(
                r"(^|-)([a-z])", lambda m: m.group(1) + m.group(2).upper(), model_id
            )
            result = result.replace("-", " ")
            result = re.sub(r"(\d+) +(\d+)", r"\1.\2", result)
        # O1 models: "o1-preview" -> "O1 Preview"
        elif model_lower.startswith("o1-"):
            result = model_id.replace("o1-", "O1-", 1)
            result = re.sub(r"-([a-z])", lambda m: f" {m.group(1).upper()}", result)
        else:
            # General case
            result = re.sub(
                r"(^|-)([a-z])", lambda m: m.group(1) + m.group(2).upper(), model_id
            )
            result = result.replace("-", " ")
            result = re.sub(r"(\d+) +(\d+)", r"\1.\2", result)

        # Clean up multiple spaces
        result = re.sub(r" +", " ", result).strip()
        return result

    def model_supports_tool_use(self, model_id: str) -> bool:
        """Check if model supports tool_use capability"""
        model_lower = model_id.lower()
        return (
            "claude" in model_lower
            or "gpt-4" in model_lower
            or "gpt-5" in model_lower
            or "o1" in model_lower
            or ("gemini" in model_lower and "gemini-pro-vision" not in model_lower)
        )

    def determine_provider(self, model_id: str) -> str:
        """Determine provider based on model ID"""
        if model_id.startswith("claude-"):
            return "anthropic"
        elif model_id == "gpt-5-mini" or model_id.startswith("azure/"):
            return "azure"
        else:
            return "openai"

    def get_context_length_for_tier(
        self, provider: str, model_id: str, tier: int
    ) -> Optional[int]:
        """Get context length based on Anthropic API tier"""
        if provider != "anthropic":
            return 128000  # Default for non-Anthropic

        is_haiku = "haiku" in model_id.lower()

        tier_configs = {
            1: {
                "haiku": 35000,  # 50k ITPM - 15k buffer
                "other": 20000,  # 30k ITPM - 10k buffer
            },
            2: {
                "haiku": 800000,  # 1M ITPM - 200k buffer
                "other": 400000,  # 500k ITPM - 100k buffer
            },
            3: {
                "haiku": 1600000,  # 2M ITPM - 400k buffer
                "other": 800000,  # 1M ITPM - 200k buffer
            },
            4: {
                "haiku": 3200000,  # 4M ITPM - 800k buffer
                "other": 1600000,  # 2M ITPM - 400k buffer
            },
        }

        config = tier_configs.get(tier, tier_configs[1])
        return config["haiku" if is_haiku else "other"]

    def generate_models_config(
        self, models: List[str], api_base: str, api_key: str, tier: int
    ) -> str:
        """Generate YAML configuration for models"""
        if not models:
            # Return empty models list if no models were fetched
            return ""

        lines = []
        for model_id in models:
            if not model_id:
                continue

            model_name = self.generate_model_name(model_id)
            provider = self.determine_provider(model_id)
            context_length = self.get_context_length_for_tier(provider, model_id, tier)

            lines.append(f"  - name: {model_name}")
            lines.append(f"    provider: {provider}")
            lines.append(f"    model: {model_id}")
            lines.append(f"    apiBase: {api_base}")
            lines.append(f"    apiKey: {api_key}")
            lines.append("    roles:")
            lines.append("      - chat")
            lines.append("      - edit")
            lines.append("      - apply")

            if self.model_supports_tool_use(model_id):
                lines.append("    capabilities:")
                lines.append("      - tool_use")

            lines.append("    defaultCompletionOptions:")
            lines.append("      maxTokens: 4096")

            if context_length:
                tier_note = f"  # Tier {tier}"
                if provider == "anthropic":
                    if "haiku" in model_id.lower():
                        {1: "50k", 2: "1M", 3: "2M", 4: "4M"}.get(tier, "50k")
                    else:
                        {1: "30k", 2: "500k", 3: "1M", 4: "2M"}.get(tier, "30k")
                    tier_note += " ITPM limit"
                lines.append(f"      contextLength: {context_length}{tier_note}")

            if provider == "anthropic":
                lines.append("      reasoning: true")
                lines.append("      reasoningBudgetTokens: 2048")
            elif provider != "azure":
                lines.append("      temperature: 0.7")
                lines.append("      topP: 0.9")

            if provider == "azure":
                lines.append("    requestOptions:")
                lines.append("      extraBodyProperties:")
                lines.append("        reasoning_effort: medium")

            lines.append("")

        return "\n".join(lines)

    def generate_config_yaml(
        self,
        models: List[str],
        api_base: str,
        api_key: str,
        tier: int,
        has_agents_md: bool,
    ) -> str:
        """Generate complete Continue.dev configuration YAML"""
        models_config = self.generate_models_config(models, api_base, api_key, tier)

        context_providers = """  - provider: diff
  - provider: url
  - provider: terminal
  - provider: code
  - provider: problems"""

        if tier > 1:
            context_providers += """
  - provider: codebase
  - provider: folder
  - provider: file"""
        else:
            context_providers += """
  # Tier 1: Large context providers DISABLED to prevent exceeding rate limits
  # - provider: codebase
  # - provider: folder
  # - provider: file"""

        # Format models section: empty array if no models, otherwise list of models
        if not models_config:
            models_section = "models: []"
        else:
            models_section = f"models:\n{models_config}"

        return f"""name: Local Config
version: 1.0.0
schema: v1

allowFileEdits: true

{models_section}

prompts: []

context:
{context_providers}
"""

    def generate_system_prompt(self, tier: int, has_agents_md: bool) -> str:
        """Generate system prompt markdown"""
        stop_rules = (
            """1. Errors found → STOP → Report → Wait (DO NOT fix automatically)
2. After completing one task → STOP → Update plan → Provide summary → Ask "Ready?"
3. Large context (>15k Sonnet/Opus, >30k Haiku) → STOP → Summary → Wait"""
            if tier == 1
            else """1. Complex errors or unclear fixes → STOP → Report → Wait
   - Fix simple errors (syntax, typos) automatically if clear"""
        )

        file_instruction = (
            "- Read only files directly related to current task (minimize context usage)"
            if tier == 1
            else ""
        )

        agents_instruction = (
            "- Read @AGENTS.md (workspace root) in FIRST request using read_file, store in session context"
            if has_agents_md
            else ""
        )

        footer = (
            "**ONE TASK PER REQUEST. ALWAYS STOP AFTER TASK.**"
            if tier == 1
            else "**Work efficiently. Stop on errors or when user requests.**"
        )

        prompt = f"""---
name: System Prompt
description: Universal system prompt optimized for API usage
---

You are an expert software development assistant.

**Core principles:**
- Write clean, maintainable, well-documented code following best practices
- Follow project conventions and existing architectural patterns
- Use Conventional Commits: type(scope): description

**🚨 STOP RULES:**
{stop_rules}

**Workflow:**
- Before starting: Read existing plan file if present
- Search first: Use codebase_search for questions
{file_instruction}
- File operations: ONE file per request
- When stopping: Provide summary in response (markdown text, NOT a file)
{agents_instruction}

{footer}
"""
        return prompt

    def run_setup_interactive(self, non_interactive: Optional[bool] = None) -> int:
        """
        Run interactive Continue.dev setup

        Args:
            non_interactive: If True, skip prompts and use values from .env. If None, check NON_INTERACTIVE env var.

        Returns:
            0 on success, 1 on failure
        """
        from ..infrastructure.output import is_non_interactive

        if non_interactive is None:
            non_interactive = is_non_interactive()

        print_header("🔧 Continue.dev Configuration Generator")
        print()

        # Try to get config from .env
        api_base, virtual_key, use_nginx = self.get_api_config_from_env()

        if non_interactive:
            # In non-interactive mode, use values from .env
            if not api_base:
                print_error("API Base URL is required but not found in .env")
                print_info("Please configure API base URL in .env or run in interactive mode")
                return 1
            if not virtual_key:
                print_error("Virtual Key is required but not found in .env")
                print_info("Please configure Virtual Key in .env or run in interactive mode")
                return 1
            print_info("Non-interactive mode: using values from .env")
        else:
            # Ask for API base URL
            print_info("📡 API Configuration")
            print()
            print_info("Enter the full API base URL for LiteLLM:")
            print_info("Examples:")
            print(
                f"  {Colors.GREEN}• http://localhost:63345/api/litellm/v1{Colors.RESET} (with Nginx, local)"
            )
            print(
                f"  {Colors.GREEN}• http://localhost:4000/v1{Colors.RESET} (direct LiteLLM, local)"
            )
            print()

            if api_base:
                suggested = api_base
                user_input = input(f"API Base URL [{suggested}]: ").strip()
                api_base = user_input if user_input else suggested
            else:
                api_base = input("API Base URL: ").strip()

            if not api_base:
                print_error("API Base URL is required")
                return 1

            api_base = api_base.rstrip("/")

            # Ask for Virtual Key
            print()
            print_info("🔑 API Key")
            print()
            print_warning("⚠️  IMPORTANT: Virtual Key is REQUIRED to access models")
            print_warning(
                "   Models are created through LiteLLM Admin UI and are only accessible via Virtual Key"
            )
            print_warning("   Master Key cannot access models created through UI")
            print()

            if virtual_key:
                masked = self.mask_api_key(virtual_key)
                print_info(
                    "Found Virtual Key in .env (press Enter to use, or enter different key):"
                )
                print_warning("Input will be hidden for security")
                import getpass

                user_input = getpass.getpass(f"Virtual Key [{masked}]: ")
                virtual_key = user_input if user_input else virtual_key
            else:
                print_warning("Input will be hidden for security")
                import getpass

                virtual_key = getpass.getpass("Virtual Key: ")

            if not virtual_key:
                print_error("Virtual Key is required")
                return 1

        print()
        print_success("✅ Configuration:")
        masked_key = self.mask_api_key(virtual_key)
        print(f"   API Base: {Colors.GREEN}{api_base}{Colors.RESET}")
        print(f"   API Key: {Colors.GREEN}{masked_key}{Colors.RESET}")
        print()

        # Ask for Anthropic tier
        print()
        print_header("📊 Anthropic API Tier Selection")
        print()
        print_info("Select your Anthropic API tier to optimize configuration:")
        print_warning(
            "Note: Tier selection applies ONLY to Anthropic models (contextLength configuration)"
        )
        # Ask for Anthropic tier
        print()
        print_header("📊 Anthropic API Tier Selection")
        print()
        print_info("Select your Anthropic API tier to optimize configuration:")
        print_warning(
            "Note: Tier selection applies ONLY to Anthropic models (contextLength configuration)"
        )
        print()
        print(
            f"{Colors.GREEN}[1] Tier 1{Colors.RESET} - Basic limits (50 RPM, 30-50k ITPM, 8-10k OTPM)"
        )
        print(
            f"{Colors.GREEN}[2] Tier 2{Colors.RESET} - Standard limits (1k RPM, 500k-1M ITPM, 50-100k OTPM)"
        )
        print(
            f"{Colors.GREEN}[3] Tier 3{Colors.RESET} - Higher limits (2k RPM, 1-2M ITPM, 100-200k OTPM)"
        )
        print(
            f"{Colors.GREEN}[4] Tier 4{Colors.RESET} - Maximum limits (4k RPM, 2-4M ITPM, 200-400k OTPM)"
        )
        print()

        if non_interactive:
            # In non-interactive mode, use tier 1 by default
            tier = 1
            print_info("Non-interactive mode: using Tier 1 (default)")
        else:
            tier_input = input("Select tier [1-4] (default: 1): ").strip()
            tier = (
                int(tier_input)
                if tier_input and tier_input.isdigit() and 1 <= int(tier_input) <= 4
                else 1
            )
            print()
            print_success(f"✅ Selected: Tier {tier}")
            print()

        # Fetch models
        print()
        print_info("🔍 Fetching models from LiteLLM API...")
        print_warning("Note: This requires Virtual Key with access to models")
        models = self.fetch_models_from_litellm(api_base, virtual_key)

        if models:
            print_success(f"✅ Found {len(models)} model(s)")
        else:
            print_warning("⚠️  Could not fetch models")
            print_info("💡 Possible reasons:")
            print_info("   • Virtual Key doesn't have access to models")
            print_info("   • Models not created yet in LiteLLM Admin UI")
            print_info("   • Network connectivity issues")
            print_info("💡 You can add models manually in the generated config file")

        # Check for AGENTS.md
        print()
        print_header("📋 AGENTS.md Configuration")
        print()
        agents_md_path = self.project_root / "AGENTS.md"
        has_agents_md = agents_md_path.exists()

        if has_agents_md:
            print_success("✅ Found AGENTS.md in repository")
        else:
            print_warning("⚠️  AGENTS.md not found in repository")
            print()
            has_agents_md = ask_yes_no(
                "Do you have AGENTS.md file in your repository?", default=False
            )

        # Generate files
        print()
        print_info("📝 Creating Continue.dev configuration...")

        # Create prompts directory
        self.output_prompts_dir.mkdir(parents=True, exist_ok=True)

        # Generate config YAML
        config_content = self.generate_config_yaml(
            models, api_base, virtual_key, tier, has_agents_md
        )
        self.output_config_file.write_text(config_content, encoding="utf-8")

        # Generate system prompt
        prompt_content = self.generate_system_prompt(tier, has_agents_md)
        self.output_system_prompt.write_text(prompt_content, encoding="utf-8")

        print_success(f"✅ Continue.dev config created at: {self.output_config_file}")
        print_success(f"✅ System prompt generated in: {self.output_prompts_dir}/")
        print("   • system-prompt.md")
        print()

        print_success("╔══════════════════════════════════════════════════════════╗")
        print_success("║  ✅ Configuration Generated Successfully!                ║")
        print_success("╚══════════════════════════════════════════════════════════╝")
        print()

        print_info("📋 Generated Files:")
        print(
            f"   Config: {Colors.GREEN}continue-dev-config-generated.yaml{Colors.RESET}"
        )
        print(
            f"   System prompt: {Colors.GREEN}.continue/prompts/system-prompt.md{Colors.RESET}"
        )
        print()

        print_info("📝 Setup steps (on client machine with VS Code):")
        print()
        print_info("1. Copy config file:")
        print(
            f"   {Colors.GREEN}cp continue-dev-config-generated.yaml <continue-dev-config-dir>/config.yaml{Colors.RESET}"
        )
        print()
        print_info("2. Enable system prompt in config.yaml:")
        print("   Edit config.yaml and uncomment:")
        print(f"   {Colors.GREEN}prompts:{Colors.RESET}")
        print(
            f"   {Colors.GREEN}  - uses: .continue/prompts/system-prompt.md{Colors.RESET}"
        )
        print()
        print_info("3. Restart VS Code/Codium and open a new chat")
        print()

        return 0
