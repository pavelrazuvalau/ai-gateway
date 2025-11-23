#!/bin/bash
# Continue.dev Configuration Generator
# Generates optimized Continue.dev configuration from LiteLLM API
# Outputs: continue-dev-config-generated.yaml and continue-dev-prompts-generated/ in project root
# Usage: bash scripts/setup_continue_dev.sh

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;93m'
BLUE='\033[1;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔧 Continue.dev Configuration Generator                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Output files in project root (will be in .gitignore)
OUTPUT_CONFIG_FILE="$PROJECT_ROOT/continue-dev-config-generated.yaml"
# Prompts will be generated in .continue/prompts/ in project root (VS Code Continue.dev looks here)
OUTPUT_PROMPTS_DIR="$PROJECT_ROOT/.continue/prompts"
OUTPUT_SYSTEM_PROMPT="$OUTPUT_PROMPTS_DIR/system-prompt.md"

# Function to read .env file
read_env_file() {
    local env_file="$1"
    local key="$2"
    if [ -f "$env_file" ]; then
        grep "^${key}=" "$env_file" | cut -d '=' -f2- | sed 's/^"//;s/"$//' | tr -d '\n'
    fi
}

# Try to get configuration from .env file
ENV_FILE="$PROJECT_ROOT/.env"
LITELLM_API_BASE=""
LITELLM_API_KEY=""
USE_NGINX=false
NGINX_PORT=""

# Ask user for full API base URL
echo -e "${BLUE}📡 API Configuration${NC}"
echo ""
echo -e "${BLUE}Enter the full API base URL for LiteLLM:${NC}"
echo -e "${YELLOW}Examples:${NC}"
echo -e "${GREEN}  • http://localhost:63345/api/litellm/v1${NC} (with Nginx, local)"
echo -e "${GREEN}  • http://YOUR_SERVER_IP:63345/api/litellm/v1${NC} (with Nginx, remote)"
echo -e "${GREEN}  • http://localhost:4000/v1${NC} (direct LiteLLM, local)"
echo -e "${GREEN}  • http://YOUR_SERVER_IP:4000/v1${NC} (direct LiteLLM, remote)"
echo -e "${GREEN}  • https://ai.example.com/api/litellm/v1${NC} (with domain)"
echo ""
read -p "API Base URL: " LITELLM_API_BASE

if [ -z "$LITELLM_API_BASE" ]; then
    echo -e "${RED}❌ API Base URL is required${NC}"
    exit 1
fi

# Remove trailing slash if present
LITELLM_API_BASE="${LITELLM_API_BASE%/}"

echo ""
echo -e "${BLUE}🔑 API Key${NC}"
echo ""
echo -e "${BLUE}Enter Virtual Key for LiteLLM:${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT: Virtual Key is REQUIRED to access models${NC}"
echo -e "${YELLOW}   Models are created through LiteLLM Admin UI and are only accessible via Virtual Key${NC}"
echo -e "${YELLOW}   Master Key cannot access models created through UI${NC}"
echo ""
echo -e "${BLUE}Virtual Key can be created in LiteLLM Admin UI:${NC}"
echo -e "${GREEN}   1. Open LiteLLM Admin UI (check your LiteLLM Admin UI URL)${NC}"
echo -e "${GREEN}   2. Go to 'Keys' section${NC}"
echo -e "${GREEN}   3. Create a new Virtual Key${NC}"
echo ""

# Try to suggest Virtual Key from .env if available (as hint only)
if [ -f "$ENV_FILE" ]; then
    SUGGESTED_VIRTUAL_KEY=$(read_env_file "$ENV_FILE" "VIRTUAL_KEY")
    
    if [ -n "$SUGGESTED_VIRTUAL_KEY" ]; then
        echo -e "${BLUE}Found Virtual Key in .env (press Enter to use, or enter different key):${NC}"
        echo -e "${YELLOW}Input will be hidden for security${NC}"
        read -s -p "Virtual Key [${SUGGESTED_VIRTUAL_KEY:0:8}...${SUGGESTED_VIRTUAL_KEY: -4}]: " LITELLM_API_KEY
        echo ""  # New line after hidden input
        LITELLM_API_KEY=${LITELLM_API_KEY:-$SUGGESTED_VIRTUAL_KEY}
    else
        echo -e "${YELLOW}Input will be hidden for security${NC}"
        read -s -p "Virtual Key: " LITELLM_API_KEY
        echo ""  # New line after hidden input
    fi
else
    echo -e "${YELLOW}Input will be hidden for security${NC}"
    read -s -p "Virtual Key: " LITELLM_API_KEY
    echo ""  # New line after hidden input
fi

if [ -z "$LITELLM_API_KEY" ]; then
    echo -e "${RED}❌ Virtual Key is required${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Configuration:${NC}"
echo -e "   API Base: ${GREEN}$LITELLM_API_BASE${NC}"
# Mask API key: show first 8 and last 4 characters
if [ ${#LITELLM_API_KEY} -gt 12 ]; then
    MASKED_KEY="${LITELLM_API_KEY:0:8}...${LITELLM_API_KEY: -4}"
else
    MASKED_KEY="${LITELLM_API_KEY:0:4}...${LITELLM_API_KEY: -2}"
fi
echo -e "   API Key: ${GREEN}$MASKED_KEY${NC}"
echo ""

# Ask user for Anthropic API Tier
echo ""
echo -e "${BLUE}📊 Anthropic API Tier Selection${NC}"
echo ""
echo -e "${BLUE}Select your Anthropic API tier to optimize configuration:${NC}"
echo -e "${YELLOW}Note: Tier selection applies ONLY to Anthropic models (contextLength configuration)${NC}"
echo -e "${YELLOW}Reference: https://platform.claude.com/docs/en/api/rate-limits${NC}"
echo ""
echo -e "${GREEN}[1] Tier 1${NC} - Basic limits (50 RPM, 30-50k ITPM, 8-10k OTPM)"
echo -e "   ${YELLOW}• Haiku 4.5: 50k ITPM${NC}"
echo -e "   ${YELLOW}• Sonnet/Opus 4.x: 30k ITPM${NC}"
echo -e "   ${YELLOW}• Recommended: Disable large context providers${NC}"
echo ""
echo -e "${GREEN}[2] Tier 2${NC} - Standard limits (1k RPM, 500k-1M ITPM, 50-100k OTPM)"
echo -e "   ${YELLOW}• Haiku 4.5: 1M ITPM${NC}"
echo -e "   ${YELLOW}• Sonnet/Opus 4.x: 500k ITPM${NC}"
echo -e "   ${YELLOW}• Recommended: Enable all context providers${NC}"
echo ""
echo -e "${GREEN}[3] Tier 3${NC} - Higher limits (2k RPM, 1-2M ITPM, 100-200k OTPM)"
echo -e "   ${YELLOW}• Haiku 4.5: 2M ITPM${NC}"
echo -e "   ${YELLOW}• Sonnet/Opus 4.x: 1M ITPM${NC}"
echo ""
echo -e "${GREEN}[4] Tier 4${NC} - Maximum limits (4k RPM, 2-4M ITPM, 200-400k OTPM)"
echo -e "   ${YELLOW}• Haiku 4.5: 4M ITPM${NC}"
echo -e "   ${YELLOW}• Sonnet/Opus 4.x: 2M ITPM${NC}"
echo ""
read -p "Select tier [1-4] (default: 1): " ANTHROPIC_TIER
ANTHROPIC_TIER=${ANTHROPIC_TIER:-1}

# Validate tier selection
if [[ ! "$ANTHROPIC_TIER" =~ ^[1-4]$ ]]; then
    echo -e "${RED}❌ Invalid tier selection. Using Tier 1 (default)${NC}"
    ANTHROPIC_TIER=1
fi

echo ""
echo -e "${GREEN}✅ Selected: Tier $ANTHROPIC_TIER${NC}"
echo ""

echo ""
echo -e "${BLUE}📝 Creating Continue.dev configuration...${NC}"

# Function to fetch models from LiteLLM API
fetch_models_from_litellm() {
    local api_base="$1"
    local api_key="$2"
    
    # Ensure base URL ends with /v1 or /api/litellm/v1 for models endpoint
    local base_url="${api_base%/}"
    if [[ "$base_url" == *"/api/litellm/v1" ]]; then
        # Nginx path - models endpoint is at /api/litellm/v1/models
        local models_url="${base_url}/models"
    elif [[ "$base_url" == *"/v1" ]]; then
        # Direct LiteLLM with /v1 - models endpoint is at /v1/models
        local models_url="${base_url}/models"
    else
        # No /v1 suffix - add it
        local models_url="${base_url}/v1/models"
    fi
    
    # Try to fetch models (no output here - output is handled by caller)
    if command -v curl &> /dev/null; then
        response=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: Bearer ${api_key}" \
            -H "Content-Type: application/json" \
            "$models_url" 2>/dev/null || echo -e "\n000")
        
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)
        
        if [ "$http_code" = "200" ] && [ -n "$body" ]; then
            # Parse JSON response and extract model IDs
            if command -v python3 &> /dev/null; then
                models=$(echo "$body" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    models = data.get('data', [])
    for model in models:
        model_id = model.get('id', '')
        if model_id:
            print(model_id)
except:
    pass
" 2>/dev/null)
                
                if [ -n "$models" ]; then
                    echo "$models"
                    return 0
                fi
            elif command -v jq &> /dev/null; then
                models=$(echo "$body" | jq -r '.data[]?.id // empty' 2>/dev/null)
                if [ -n "$models" ]; then
                    echo "$models"
                    return 0
                fi
            fi
        # Note: Error messages are handled by caller, not here
        fi
    elif command -v wget &> /dev/null; then
        # Fallback to wget
        response=$(wget -qO- --header="Authorization: Bearer ${api_key}" \
            --header="Content-Type: application/json" \
            "$models_url" 2>/dev/null || echo "")
        
        if [ -n "$response" ] && command -v python3 &> /dev/null; then
            models=$(echo "$response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    models = data.get('data', [])
    for model in models:
        model_id = model.get('id', '')
        if model_id:
            print(model_id)
except:
    pass
" 2>/dev/null)
            
            if [ -n "$models" ]; then
                echo "$models"
                return 0
            fi
        fi
    fi
    
    return 1
}

# Fetch models from LiteLLM
MODELS_LIST=""
if [ -n "$LITELLM_API_BASE" ] && [ -n "$LITELLM_API_KEY" ]; then
    echo "" >&2
    echo -e "${BLUE}🔍 Fetching models from LiteLLM API...${NC}" >&2
    echo -e "${YELLOW}Note: This requires Virtual Key with access to models${NC}" >&2
    # Build URL for display
    if [[ "$LITELLM_API_BASE" == */v1 ]]; then
        models_display_url="${LITELLM_API_BASE}/models"
    else
        models_display_url="${LITELLM_API_BASE}/v1/models"
    fi
    echo -e "   URL: ${GREEN}$models_display_url${NC}" >&2
    MODELS_LIST=$(fetch_models_from_litellm "$LITELLM_API_BASE" "$LITELLM_API_KEY")
    
    if [ -n "$MODELS_LIST" ]; then
        model_count=$(echo "$MODELS_LIST" | wc -l | tr -d ' ')
        echo -e "${GREEN}✅ Found $model_count model(s)${NC}" >&2
    else
        echo -e "${YELLOW}⚠️  Could not fetch models${NC}" >&2
        echo -e "${BLUE}💡 Possible reasons:${NC}" >&2
        echo -e "   • Virtual Key doesn't have access to models" >&2
        echo -e "   • Models not created yet in LiteLLM Admin UI" >&2
        echo -e "   • Network connectivity issues" >&2
        echo -e "${BLUE}💡 You can add models manually in the generated config file${NC}" >&2
    fi
fi

# Check if AGENTS.md exists in repository
echo "" >&2
echo -e "${BLUE}📋 AGENTS.md Configuration${NC}" >&2
echo "" >&2
echo -e "${YELLOW}Standard: AGENTS.md${NC}" >&2
echo -e "${GREEN}  • AGENTS.md is an open standard used by 20k+ projects${NC}" >&2
echo -e "${GREEN}  • It's a dedicated file for AI coding agents (like a README for agents)${NC}" >&2
echo -e "${GREEN}  • Learn more: https://agents.md/#examples${NC}" >&2
echo "" >&2

# Check if AGENTS.md exists in project root
HAS_AGENTS_MD="n"
if [ -f "$PROJECT_ROOT/AGENTS.md" ]; then
    HAS_AGENTS_MD="y"
    echo -e "${GREEN}✅ Found AGENTS.md in repository${NC}" >&2
else
    echo -e "${YELLOW}⚠️  AGENTS.md not found in repository${NC}" >&2
    echo "" >&2
    read -p "Do you have AGENTS.md file in your repository? (y/n) [n]: " HAS_AGENTS_MD
    HAS_AGENTS_MD=${HAS_AGENTS_MD:-n}
fi

if [[ "$HAS_AGENTS_MD" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}✅ System prompt will include instructions to read AGENTS.md${NC}" >&2
    echo -e "${BLUE}ℹ️  Agent will read @AGENTS.md in first request. Content stored in session context.${NC}" >&2
else
    echo -e "${BLUE}ℹ️  System prompt will be used without AGENTS.md instructions${NC}" >&2
fi


# Function to generate model name from model ID
generate_model_name() {
    local model_id="$1"
    local model_lower=$(echo "$model_id" | tr '[:upper:]' '[:lower:]')
    local result=""
    
    # Special handling for GPT models: keep GPT uppercase and preserve dash before version
    if [[ "$model_lower" == gpt-* ]]; then
        # e.g., "gpt-5-mini" -> "GPT-5 Mini"
        result=$(echo "$model_id" | sed -E 's/^gpt-/GPT-/i' | sed -E 's/-([a-z])/ \u\1/g')
    # Special handling for Claude models: combine version numbers with dot
    elif [[ "$model_lower" == claude-* ]]; then
        # e.g., "claude-haiku-4-5" -> "Claude Haiku 4.5"
        # First capitalize words
        result=$(echo "$model_id" | sed -E 's/(^|-)([a-z])/\1\u\2/g' | sed 's/-/ /g')
        # Combine consecutive numbers with dot: "4 5" -> "4.5"
        result=$(echo "$result" | sed -E 's/([0-9]) +([0-9])/\1.\2/g')
    # Special handling for O1 models: keep O1 uppercase
    elif [[ "$model_lower" == o1-* ]]; then
        # e.g., "o1-preview" -> "O1 Preview"
        result=$(echo "$model_id" | sed -E 's/^o1-/O1-/i' | sed -E 's/-([a-z])/ \u\1/g')
    # General case: capitalize words, convert dashes to spaces
    else
        result=$(echo "$model_id" | sed -E 's/(^|-)([a-z])/\1\u\2/g' | sed 's/-/ /g')
        # Try to combine version numbers: "4 5" -> "4.5"
        result=$(echo "$result" | sed -E 's/([0-9]) +([0-9])/\1.\2/g')
    fi
    
    # Clean up multiple spaces
    result=$(echo "$result" | sed 's/  */ /g' | sed 's/^ *//;s/ *$//')
    
    echo "$result"
}

# Function to check if model supports tool_use
model_supports_tool_use() {
    local model_id="$1"
    model_lower=$(echo "$model_id" | tr '[:upper:]' '[:lower:]')
    
    # Models that typically support tool_use
    if [[ "$model_lower" == *"claude"* ]] || \
       [[ "$model_lower" == *"gpt-4"* ]] || \
       [[ "$model_lower" == *"gpt-5"* ]] || \
       [[ "$model_lower" == *"o1"* ]] || \
       [[ "$model_lower" == *"gemini"* ]] && [[ "$model_lower" != *"gemini-pro-vision"* ]]; then
        return 0
    fi
    return 1
}

# Function to escape YAML string for systemMessage
escape_yaml_string() {
    local str="$1"
    # Escape backslashes and newlines for YAML literal block
    echo "$str" | sed 's/\\/\\\\/g' | sed ':a;N;$!ba;s/\n/\\n/g'
}

# Determine provider based on model ID
# This function detects the actual provider (azure, anthropic, openai) based on model name
# Continue.dev uses provider to determine which API format to use
determine_provider() {
    local model_id="$1"
    
    # Claude models use Anthropic native API
    if [[ "$model_id" =~ ^claude- ]]; then
        echo "anthropic"
        return
    fi
    
    # Azure OpenAI models (known Azure deployments)
    # Note: gpt-5-mini is deployed via Azure OpenAI in this setup
    if [[ "$model_id" == "gpt-5-mini" ]] || [[ "$model_id" =~ ^azure/ ]]; then
        echo "azure"
        return
    fi
    
    # Default to OpenAI-compatible (works with LiteLLM OpenAI-compatible endpoint)
    echo "openai"
}

# Generate models configuration dynamically
generate_models_config() {
    if [ -n "$MODELS_LIST" ]; then
        # Generate models from fetched list
        while IFS= read -r model_id; do
            [ -z "$model_id" ] && continue
            
            model_name=$(generate_model_name "$model_id")
            provider=$(determine_provider "$model_id")
            
            echo "  - name: $model_name"
            echo "    provider: $provider"
            echo "    model: $model_id"
            echo "    apiBase: $LITELLM_API_BASE"
            echo "    apiKey: $LITELLM_API_KEY"
            echo "    roles:"
            echo "      - chat"
            echo "      - edit"
            echo "      - apply"
            
            if model_supports_tool_use "$model_id"; then
                echo "    capabilities:"
                echo "      - tool_use"
            fi
            
            # Add defaultCompletionOptions for model parameters
            echo "    defaultCompletionOptions:"
            echo "      maxTokens: 4096"
            
            # Limit context length to prevent exceeding rate limits
            # NOTE: Tier-based configuration applies ONLY to Anthropic models
            # For other providers (Azure, OpenAI, etc.), default contextLength is used
            # Context length is set based on Anthropic API tier and model
            # Buffer is added for summarize context, new files, and conversation history
            # Note: Only uncached input tokens count towards ITPM (cache-aware)
            # Reference: https://platform.claude.com/docs/en/api/rate-limits
            if [[ "$provider" == "anthropic" ]]; then
                # Check if it's Haiku or Sonnet/Opus
                if [[ "$model_id" =~ ^claude-haiku ]]; then
                    # Haiku 4.5 limits by tier
                    case "$ANTHROPIC_TIER" in
                        1)
                            # Tier 1: 50k ITPM - set to 35k (15k buffer)
                            echo "      contextLength: 35000  # Tier 1: 50k ITPM limit - 15k buffer"
                            ;;
                        2)
                            # Tier 2: 1M ITPM - set to 800k (200k buffer)
                            echo "      contextLength: 800000  # Tier 2: 1M ITPM limit - 200k buffer"
                            ;;
                        3)
                            # Tier 3: 2M ITPM - set to 1.6M (400k buffer)
                            echo "      contextLength: 1600000  # Tier 3: 2M ITPM limit - 400k buffer"
                            ;;
                        4)
                            # Tier 4: 4M ITPM - set to 3.2M (800k buffer)
                            echo "      contextLength: 3200000  # Tier 4: 4M ITPM limit - 800k buffer"
                            ;;
                    esac
                else
                    # Sonnet/Opus 4.x limits by tier
                    case "$ANTHROPIC_TIER" in
                        1)
                            # Tier 1: 30k ITPM - set to 20k (10k buffer)
                            echo "      contextLength: 20000  # Tier 1: 30k ITPM limit - 10k buffer"
                            ;;
                        2)
                            # Tier 2: 500k ITPM - set to 400k (100k buffer)
                            echo "      contextLength: 400000  # Tier 2: 500k ITPM limit - 100k buffer"
                            ;;
                        3)
                            # Tier 3: 1M ITPM - set to 800k (200k buffer)
                            echo "      contextLength: 800000  # Tier 3: 1M ITPM limit - 200k buffer"
                            ;;
                        4)
                            # Tier 4: 2M ITPM - set to 1.6M (400k buffer)
                            echo "      contextLength: 1600000  # Tier 4: 2M ITPM limit - 400k buffer"
                            ;;
                    esac
                fi
            else
                # For non-Anthropic providers (Azure, OpenAI, etc.), use reasonable default
                # Tier selection does not apply to these providers
                echo "      contextLength: 128000  # Default context length for non-Anthropic models (adjust based on provider limits)"
            fi
            
            # Anthropic-specific: enable reasoning/thinking
            # Note: temperature must be 1 or omitted when thinking is enabled
            # See: https://docs.claude.com/en/docs/build-with-claude/extended-thinking
            if [[ "$provider" == "anthropic" ]]; then
                echo "      reasoning: true"
                echo "      reasoningBudgetTokens: 2048"
                echo "      # Note: temperature must be 1 or omitted when thinking is enabled"
            # Azure reasoning models (GPT-5, o1, o3) don't support temperature/topP
            # See: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning
            elif [[ "$provider" != "azure" ]]; then
                # For other providers (OpenAI-compatible), set temperature/topP
                echo "      temperature: 0.7"
                echo "      topP: 0.9"
            fi
            
            # Retry configuration is handled by LiteLLM (router_settings.num_retries: 5, retry_after: 120)
            # LiteLLM callback automatically overrides max_retries=0 from Continue.dev to enable retries
            # No need to configure retry in Continue.dev - LiteLLM handles it with delays and exponential backoff
            if [[ "$provider" == "azure" ]]; then
                # Azure-specific: reasoning_effort is a direct request parameter for Azure reasoning models
                # Pass it via requestOptions.extraBodyProperties (Continue.dev merges it into request body)
                # See Azure docs: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning
                echo "    requestOptions:"
                echo "      extraBodyProperties:"
                echo "        reasoning_effort: medium"
                echo "    # Note: reasoning_effort values: low, medium, high (or minimal for GPT-5)"
                echo "    # Azure reasoning models don't support temperature/topP - removed from config"
                echo "    # See: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning"
            fi
            
            # Note: systemMessage is removed - it doesn't work in Continue.dev
            # Use prompts instead (see prompts section in config)
            
            echo ""
        done <<< "$MODELS_LIST"
    else
        # Fallback: default models if API fetch failed
        cat << EOF
  - name: Claude Haiku 4.5
    provider: anthropic
    model: claude-haiku-4-5
    apiBase: $LITELLM_API_BASE
    apiKey: $LITELLM_API_KEY
    roles:
      - chat
      - edit
      - apply
    capabilities:
      - tool_use
    defaultCompletionOptions:
      maxTokens: 4096
EOF
        # Set contextLength based on tier
        case "$ANTHROPIC_TIER" in
            1)
                echo "      contextLength: 35000  # Tier 1: 50k ITPM limit - 15k buffer"
                ;;
            2)
                echo "      contextLength: 800000  # Tier 2: 1M ITPM limit - 200k buffer"
                ;;
            3)
                echo "      contextLength: 1600000  # Tier 3: 2M ITPM limit - 400k buffer"
                ;;
            4)
                echo "      contextLength: 3200000  # Tier 4: 4M ITPM limit - 800k buffer"
                ;;
        esac
        cat << EOF
      reasoning: true
      reasoningBudgetTokens: 2048
      # Note: temperature must be 1 or omitted when thinking is enabled
      # See: https://docs.claude.com/en/docs/build-with-claude/extended-thinking
      # Tier $ANTHROPIC_TIER limits: See https://platform.claude.com/docs/en/api/rate-limits
    # Note: Retry configuration is handled by LiteLLM (router_settings.num_retries: 5, retry_after: 120)
    # LiteLLM callback automatically overrides max_retries=0 from Continue.dev to enable retries
    # Note: systemMessage removed - use prompts instead
    # Note: provider: anthropic enables native Anthropic API via /v1/messages endpoint

  - name: GPT-5 Mini
    provider: azure
    model: gpt-5-mini
    apiBase: $LITELLM_API_BASE
    apiKey: $LITELLM_API_KEY
    roles:
      - chat
      - edit
      - apply
    capabilities:
      - tool_use
    defaultCompletionOptions:
      maxTokens: 4096
      # Note: temperature and topP are NOT supported for Azure reasoning models (GPT-5, o1, o3)
      # See: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning
    requestOptions:
      # Note: Retry configuration is handled by LiteLLM (router_settings.num_retries: 5, retry_after: 120)
      # LiteLLM callback automatically overrides max_retries=0 from Continue.dev to enable retries
      extraBodyProperties:
        reasoning_effort: medium
    # Note: systemMessage removed - use prompts instead
    # Note: provider: azure indicates Azure OpenAI deployment (LiteLLM handles API conversion)
    # Note: reasoning_effort values: low, medium, high (or minimal for GPT-5)
    # See Azure docs: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning
EOF
    fi
}

# Create optimized config (YAML format) with dynamic models
{
    cat << EOF
name: Local Config
version: 1.0.0
schema: v1

# Global settings
allowFileEdits: true  # Allow file edits without confirmation prompts

# Models configuration (auto-generated from LiteLLM API)
# Note: systemMessage is NOT used - it doesn't work in Continue.dev (confirmed via logs)
# Use prompts instead (see prompts section below)
models:
$(generate_models_config)

# System prompt configuration
# System prompt is generated in .continue/prompts/ in project root
# Continue.dev VS Code extension will find it automatically when working in this project
# Uncomment the line below to enable:
# - uses: .continue/prompts/system-prompt.md
# 
# Alternative: You can also use just the filename if prompt is in .continue/prompts/:
# - uses: system-prompt
# 
# Note: systemMessage in models config doesn't work (confirmed via logs)
# Prompts are the recommended way to add instructions to Continue.dev
# See: https://docs.continue.dev/customize/deep-dives/prompts
# 
# AGENTS.md handling (if file exists):
# - System prompt will instruct agent to read @AGENTS.md in the FIRST request
# - Content is stored in session context, not sent with every request
# - Low token usage: ~2k-5k tokens per request after first
# - Large AGENTS.md files are OK (no size limit)
prompts: []

context:
  # Context providers - array format required by Continue.dev
  # Exclusions can be handled via .continueignore file (optional, created manually if needed)
  # 
  # NOTE: Tier selection applies ONLY to Anthropic models for contextLength configuration
  # Context providers below are GLOBAL and affect ALL models in Continue.dev
  # Configuration optimized for Anthropic API Tier $ANTHROPIC_TIER
  # Reference: https://platform.claude.com/docs/en/api/rate-limits
  # 
  # Safe to keep (small context):
  - provider: diff
  - provider: url
  - provider: terminal
  - provider: code
  - provider: problems
EOF

    # Add context providers based on Anthropic tier
    # Note: This is a global setting affecting all models, but optimized for Anthropic Tier limits
    if [ "$ANTHROPIC_TIER" -eq 1 ]; then
        # Tier 1: Disable large context providers to prevent exceeding Anthropic rate limits
        cat << EOF
  # 
  # Anthropic Tier 1: Large context providers DISABLED to prevent exceeding rate limits
  # Real usage data shows max context can reach 81k tokens (Haiku) on vibe coding projects
  # Tier 1 limits: Haiku 50k ITPM, Sonnet/Opus 30k ITPM
  # Disabling these providers helps stay within Anthropic limits (affects all models):
  # - provider: codebase  # DISABLED for Tier 1 - Auto-includes code files (can be very large)
  # - provider: folder     # DISABLED for Tier 1 - Auto-includes folder contents (can be very large)
  # - provider: file       # DISABLED for Tier 1 - Auto-includes file contents (can be large)
  # 
  # To enable: Uncomment the providers above if you upgrade to Tier 2+
  # Note: If you use non-Anthropic models with higher limits, you may want to enable these
EOF
    else
        # Tier 2+: Enable all context providers
        cat << EOF
  # 
  # Anthropic Tier $ANTHROPIC_TIER: All context providers ENABLED
  # Higher tier limits allow for larger context windows
  # Note: This affects all models, not just Anthropic
  - provider: codebase  # Auto-includes relevant code files
  - provider: folder     # Auto-includes folder contents
  - provider: file       # Auto-includes file contents when referenced
EOF
    fi
} > "$OUTPUT_CONFIG_FILE"

echo -e "${GREEN}✅ Continue.dev config created at: $OUTPUT_CONFIG_FILE${NC}" >&2

# Always generate system prompt (system prompt is always used)
# Create prompts directory
mkdir -p "$OUTPUT_PROMPTS_DIR"

# Generate system-prompt.md (universal prompt - works in any project)
# Optimized for token efficiency based on Anthropic API tier
# Removed meta-information, technical details, and redundant instructions
{
    cat << 'PROMPT_HEADER'
---
name: System Prompt
description: Universal system prompt optimized for API usage
---

You are an expert software development assistant.

**Core principles:**
- Write clean, maintainable, well-documented code following best practices
- Follow project conventions and existing architectural patterns
- Use Conventional Commits: type(scope): description

**🚨 STOP RULES:**
PROMPT_HEADER

    # Add tier-specific error handling rules
    if [ "$ANTHROPIC_TIER" -eq 1 ]; then
        # Tier 1: Strict control needed (small context)
        cat << 'PROMPT_TIER1_STOP'
1. Errors found → STOP → Report → Wait (DO NOT fix automatically)
2. After completing one task → STOP → Update plan → Provide summary → Ask "Ready?"
3. Large context (>15k Sonnet/Opus, >30k Haiku) → STOP → Summary → Wait
PROMPT_TIER1_STOP
    else
        # Tier 2+: Flexible approach (large context allows more autonomy)
        cat << 'PROMPT_TIER2_STOP'
1. Complex errors or unclear fixes → STOP → Report → Wait
   - Fix simple errors (syntax, typos) automatically if clear
PROMPT_TIER2_STOP
    fi

    cat << 'PROMPT_WORKFLOW'
**Workflow:**
- Before starting: Read existing plan file if present
- Search first: Use codebase_search for questions
PROMPT_WORKFLOW

    # Add tier-specific file reading instruction
    if [ "$ANTHROPIC_TIER" -eq 1 ]; then
        cat << 'PROMPT_TIER1_FILES'
- Read only files directly related to current task (minimize context usage)
PROMPT_TIER1_FILES
    fi

    cat << 'PROMPT_WORKFLOW_CONT'
- File operations: ONE file per request
- When stopping: Provide summary in response (markdown text, NOT a file)
PROMPT_WORKFLOW_CONT

    # Conditionally include AGENTS.md instructions (optimized: brief but effective)
    if [[ "$HAS_AGENTS_MD" =~ ^[Yy]$ ]]; then
        cat << 'PROMPT_AGENTS'
- Read @AGENTS.md (workspace root) in FIRST request using read_file, store in session context
PROMPT_AGENTS
    fi

    # Add tier-specific footer
    if [ "$ANTHROPIC_TIER" -eq 1 ]; then
        # Tier 1: Strict control
        cat << 'PROMPT_FOOTER_TIER1'
**ONE TASK PER REQUEST. ALWAYS STOP AFTER TASK.**
PROMPT_FOOTER_TIER1
    else
        # Tier 2+: More flexible (large context allows more work per request)
        cat << 'PROMPT_FOOTER_TIER2'
**Work efficiently. Stop on errors or when user requests.**
PROMPT_FOOTER_TIER2
    fi
} > "$OUTPUT_SYSTEM_PROMPT"

echo -e "${GREEN}✅ System prompt generated in: $OUTPUT_PROMPTS_DIR/${NC}" >&2
echo -e "   • system-prompt.md" >&2

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Configuration Generated Successfully!                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Generated Files:${NC}" >&2
echo -e "   Config: ${GREEN}continue-dev-config-generated.yaml${NC}" >&2
echo -e "   System prompt: ${GREEN}.continue/prompts/system-prompt.md${NC}" >&2
echo -e "   ${YELLOW}Note: Prompt is in project directory - Continue.dev will find it automatically${NC}" >&2
echo "" >&2
echo -e "${BLUE}📝 Setup steps (on client machine with VS Code):${NC}" >&2
echo "" >&2

echo -e "${BLUE}1. Copy config file:${NC}" >&2
echo -e "   ${GREEN}cp continue-dev-config-generated.yaml <continue-dev-config-dir>/config.yaml${NC}" >&2
echo -e "   ${YELLOW}Note: Continue.dev config directory is usually ~/.continue/ (Linux/macOS) or %USERPROFILE%/.continue/ (Windows)${NC}" >&2
echo "" >&2

echo -e "${BLUE}2. Enable system prompt in config.yaml:${NC}" >&2
echo -e "   Edit <continue-dev-config-dir>/config.yaml and uncomment:${NC}" >&2
echo -e "   ${GREEN}prompts:${NC}" >&2
echo -e "   ${GREEN}  - uses: .continue/prompts/system-prompt.md${NC}" >&2
echo -e "   ${YELLOW}Or use short name if prompt is in .continue/prompts/:${NC}" >&2
echo -e "   ${GREEN}  - uses: system-prompt${NC}" >&2
echo "" >&2

echo -e "${BLUE}3. Verify configuration:${NC}" >&2
echo -e "   • Check API keys in config.yaml" >&2
echo -e "   • Verify apiBase URL (current: $LITELLM_API_BASE)" >&2
echo "" >&2

echo -e "${BLUE}4. Restart VS Code/Codium and open a new chat${NC}" >&2
if [[ "$HAS_AGENTS_MD" =~ ^[Yy]$ ]]; then
    echo -e "   ${YELLOW}Tip: System prompt will instruct agent to read AGENTS.md automatically in first request${NC}" >&2
fi
echo "" >&2

echo -e "${BLUE}💡 Configuration features:${NC}" >&2
echo -e "   • System prompt included (sent with every request, ~500-1000 tokens)" >&2
if [[ "$HAS_AGENTS_MD" =~ ^[Yy]$ ]]; then
    echo -e "   • AGENTS.md: Agent will read @AGENTS.md in first request" >&2
    echo -e "   • ${GREEN}✅ Content stored in session context, not sent with every request${NC}" >&2
    echo -e "   • ${GREEN}✅ Low token usage: ~2k-5k tokens per request after first${NC}" >&2
else
    echo -e "   • No AGENTS.md configured - using system prompt only" >&2
fi
echo -e "   • Other context providers (codebase, diff, etc.) still work normally" >&2
if [ -n "$MODELS_LIST" ]; then
    echo -e "   • Models auto-configured from LiteLLM API (no manual editing needed)" >&2
fi
echo "" >&2

