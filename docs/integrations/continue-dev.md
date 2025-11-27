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

## Correct Provider Configuration

**⚠️ Important lesson:** The problem may not be where it seems. Always verify your provider configuration.

### Understanding Provider Configuration

**LiteLLM is OpenAI-compatible, but the provider must be the real provider name:**

- ✅ **Correct:** `provider: anthropic` for Claude models
- ✅ **Correct:** `provider: azure` for Azure OpenAI models
- ✅ **Correct:** `provider: openai` for OpenAI GPT models
- ❌ **Incorrect:** `provider: openai` for ALL models (common mistake)

### How Provider is Determined

The Continue.dev setup script automatically determines the provider based on model ID:

- **Claude models** (starting with `claude-`): `provider: anthropic`
- **Azure models** (`gpt-5-mini` or starting with `azure/`): `provider: azure`
- **Other models** (GPT, etc.): `provider: openai`

### Why This Matters

**LiteLLM provides OpenAI-compatible API, but internally uses real provider names:**

- Each provider has different capabilities (tool use, reasoning, etc.)
- Provider-specific features require correct provider name
- Incorrect provider name may cause tool-call-filter errors or missing features

### Common Configuration Errors

**Error:** Specifying `openai` as provider for all models

**Why it's wrong:**
- Claude models need `provider: anthropic` for proper tool use support
- Azure models need `provider: azure` for Azure-specific features
- Using wrong provider may cause features to not work correctly

**Correct solution:**
- Let the setup script automatically determine provider (recommended)
- Or manually specify the real provider name based on model ID

### Examples of Correct Configuration

**Anthropic (Claude):**
```yaml
models:
  - title: Claude Sonnet 4.5
    provider: anthropic  # ✅ Correct
    model: claude-sonnet-4-5
    apiBase: http://localhost:PORT/api/litellm/v1
```

**Azure OpenAI:**
```yaml
models:
  - title: GPT-5 Mini
    provider: azure  # ✅ Correct
    model: gpt-5-mini
    apiBase: http://localhost:PORT/api/litellm/v1
```

**OpenAI (GPT):**
```yaml
models:
  - title: GPT-4o
    provider: openai  # ✅ Correct
    model: gpt-4o
    apiBase: http://localhost:PORT/api/litellm/v1
```

**Related:** [Troubleshooting - Common Configuration Errors](../troubleshooting.md#common-configuration-errors)

## Practical Limitations of Anthropic API Tier 1

**⚠️ Important for beginners:** If you're using Anthropic API Tier 1, be aware of practical limitations that affect your workflow with Continue.dev.

### What is Tier 1?

Anthropic API Tier 1 is the default tier for new accounts. It has:
- **Rate limits:** 50,000 input tokens per minute (ITPM) for Haiku, 30k ITPM for Sonnet/Opus
- **Strict enforcement:** Rate limits are actively enforced
- **Retry delays:** Usually 60 seconds when limit is hit

### Practical Limitations with Continue.dev

**Tier 1 makes work possible, but not comfortable:**

1. **Rate limits are restrictive:**
   - Frequent 429 errors during active coding sessions
   - Long wait times (60+ seconds) when limits are hit
   - Automatic retries help, but requests take longer
   - Code completion and suggestions may be delayed

2. **System prompts help, but don't guarantee compliance:**
   - System prompts can guide model behavior
   - However, models may not always follow instructions exactly
   - You must actively manage context and conversation flow
   - Model may not always follow your coding style preferences

3. **Context management is critical:**
   - You must actively manage conversation context
   - **Context summary feature is critically important** for Tier 1
   - Without proper context management, you'll hit rate limits more often
   - Large codebases may require frequent context summarization

4. **For comfortable work, Tier 2+ is recommended:**
   - Tier 2+ has higher rate limits (500k-4M ITPM)
   - Less frequent rate limit errors
   - Better experience for active AI coding assistance
   - More reliable code completion and suggestions

### Recommendations for Tier 1 Users

- **For testing/learning:** Tier 1 is sufficient
- **For active development:** Consider upgrading to Tier 2+
- **Use context summary:** Critical feature for managing long conversations
- **Monitor usage:** Check LiteLLM Admin UI for rate limit patterns
- **Understand retry behavior:** Requests may take longer due to automatic retries
- **Be patient:** Code suggestions may take longer during active use

**Note:** This information is based on practical experience with Anthropic API Tier 1. Rate limits and behavior may vary. Check [Anthropic API documentation](https://docs.anthropic.com/claude/docs/rate-limits) for current limits.

**Related:** [Troubleshooting - Practical Limitations of Anthropic API Tier 1](../troubleshooting.md#practical-limitations-of-anthropic-api-tier-1)

