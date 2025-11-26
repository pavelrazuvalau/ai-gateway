# Continue.dev Integration

AI Gateway includes a Python service to generate optimized Continue.dev configuration for VS Code extension. The service is accessible via CLI command or bash wrapper script.

## ⚠️ CRITICAL: Prerequisites (Must Complete First!)

**Before running the Continue.dev setup script, you MUST complete these steps in order:**

### 1. ✅ AI Gateway Running
```bash
./start.sh  # Linux/macOS
start.bat    # Windows
```
Containers must be running and healthy.

### 2. ✅ Virtual Key Created (REQUIRED)
**Virtual Key is MANDATORY** - Continue.dev setup will fail without it.

**Create Virtual Key:**
```bash
./virtual-key.sh  # Linux/macOS
virtual-key.bat   # Windows
```

**Why it's required:**
- Continue.dev setup fetches models from LiteLLM API (`/v1/models` endpoint)
- API requires authentication (Virtual Key or Master Key)
- Virtual Key is more secure than Master Key for API access
- Script uses Virtual Key from `.env` file automatically

**Verify Virtual Key exists:**
```bash
grep VIRTUAL_KEY .env
# Should show: VIRTUAL_KEY=sk-xxxxxxxxxxxxx
```

### 3. ✅ Providers Configured
- Open LiteLLM Admin UI: http://localhost:4000/ui
- Add your API keys (Anthropic, OpenAI, Azure, etc.)
- See [Getting Started Guide](../getting-started.md#step-32-add-providers)

### 4. ✅ Models Added
- In LiteLLM Admin UI, go to Models section
- Add models for your providers
- Models must be saved and visible in LiteLLM UI
- See [Getting Started Guide](../getting-started.md#step-33-add-models)

**⚠️ If you skip any step, Continue.dev setup will fail!**

**Why these prerequisites?** 

The Continue.dev setup script:
1. **Fetches models from LiteLLM API** (`/v1/models` endpoint) using Virtual Key
2. **Requires Virtual Key** for API authentication (stored in `.env` file)
3. **Needs models to exist** in LiteLLM to generate configuration
4. **Needs providers configured** so models are available

If any prerequisite is missing, the script will fail with clear error messages.

## Quick Setup

**Step 1:** Make sure models are configured (see [Getting Started](../getting-started.md#step-3-access-and-configure))

**Step 2:** Run the setup (choose one method):

```bash
# Method 1: Via CLI (recommended)
./ai-gateway continue-dev

# Method 2: Via bash wrapper script
./continue-dev.sh
```

The service will:
- ✅ Fetch models dynamically from LiteLLM API via Virtual Key (requires models to be configured)
- ✅ Generate optimized configuration with proper roles (chat, edit, apply)
- ✅ Create system prompts in `.continue/prompts/` directory
- ✅ Configure AGENTS.md handling (optional)
- ✅ Optimize context length based on Anthropic API tier

## Generated Files

- `continue-dev-config-generated.yaml` - Continue.dev configuration (in `.gitignore`)
- `.continue/prompts/system-prompt.md` - System prompt for agents (in `.gitignore`)

**Note:** Generated files are excluded from git. Copy `continue-dev-config-generated.yaml` to your Continue.dev config directory (usually `~/.continue/`).

## When to Run the Script

**Recommended workflow:**
1. Complete initial setup (`./setup.sh`)
2. Start containers (`./start.sh`)
3. Configure providers and models in LiteLLM Admin UI
4. Create Virtual Key in LiteLLM Admin UI
5. **Then** run Continue.dev setup:
   ```bash
   ./ai-gateway continue-dev
   # Or: ./continue-dev.sh
   ```

**You can skip Continue.dev setup during initial setup** - it can be done anytime after models are configured.

**Note**: The setup will automatically check if models are available via Virtual Key after containers start. If models are found, you'll be prompted to configure Continue.dev.

## Features

- **Automatic model discovery** - No need to manually configure models
- **Tier-based configuration** - Optimized system prompts and context length based on Anthropic API tier (1-4)
- **Optimized for token usage** - Tier-specific prompts (Tier 1: strict control, Tier 2+: flexible approach)
- **AGENTS.md support** - Optional integration with project documentation
- **Context providers management** - Automatically disabled for Tier 1, enabled for Tier 2+ to prevent rate limit issues

## Anthropic API Tier Selection

The script will prompt you to select your Anthropic API tier (1-4) based on your account limits:
- **Tier 1**: Strict control, limited context providers (50k ITPM for Haiku, 30k for Sonnet/Opus)
- **Tier 2+**: Flexible approach, all context providers enabled (500k-4M ITPM)

**Architecture**: The bash script `continue-dev.sh` is a wrapper that sets up Python virtual environment and calls the Python service (`ContinueDevService` in `src/application/continue_dev_service.py`). All business logic is in Python.

