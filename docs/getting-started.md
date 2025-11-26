# Getting Started Guide

<!--
Tags for AI agents:
- getting-started
- installation
- setup
- configuration
- virtual-key
- models
- troubleshooting
- quick-start
-->

Complete setup and launch guide for AI Gateway. This guide will help you get AI Gateway running in about 5 minutes.

## Quick Links

- **[Step 1: Run Setup](#step-1-run-setup-script)** - Initial configuration
- **[Step 2: Start System](#step-2-start-the-system)** - Launch containers
- **[Step 3: Create Virtual Key](#step-3-create-virtual-key)** - Set up authentication
- **[Step 4: Configure Models](#step-4-configure-models)** - Add providers and models
- **[Step 5: First Use](#step-5-first-use)** - Start using AI Gateway
- **[Troubleshooting](#troubleshooting)** - Common issues and solutions

**Related Documentation:**
- [Configuration Guide](configuration.md) - Ports, resources, budgets
- [System Requirements](system-requirements.md) - Hardware requirements
- [API for Agents](integrations/api-for-agents.md) - API integration
- [Examples](examples/README.md) - Code examples

## Quick Overview

AI Gateway bundles LiteLLM, Open WebUI, PostgreSQL, and Nginx into a single, easy-to-configure package. After setup, you'll have:

- **Open WebUI** - Modern web interface for chatting with AI models
- **LiteLLM API** - Unified API proxy for multiple LLM providers
- **LiteLLM Admin UI** - Interface for managing providers, models, and settings
- **PostgreSQL** - Database for storing configurations and usage data

## Prerequisites

Before starting, make sure you have:

- **Python**: 3.8 or higher
- **Docker**: 20.10 or higher (Docker Compose v2 recommended)
- **RAM**: 3GB minimum (4GB recommended)
- **OS**: Linux (tested), macOS/Windows (experimental)

📖 For detailed requirements and resource profiles, see [System Requirements](system-requirements.md)

### Checking Dependencies

Verify that Docker is installed and running:

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker is running
docker ps
```

If Docker is not installed or not running, see [If Dependencies Are Missing](#if-dependencies-are-missing) below.

## Step 1: Run Setup Script {#step-1-run-setup-script}

The setup script configures your AI Gateway installation with resource profiles, ports, and security settings.

### Linux/macOS

```bash
./setup.sh
```

Or using the CLI:

```bash
./ai-gateway setup
```

### Windows

```cmd
setup.bat
```

Or using Python directly:

```cmd
python ai-gateway setup
```

### What the Setup Does

The setup script will guide you through:

1. **Resource Profile Selection**
   - **Desktop** - Unlimited resources for local development
   - **Small VPS** - 2GB RAM, 2 CPU cores (⚠️ tight, see [System Requirements](system-requirements.md))
   - **Medium VPS** - 4GB RAM, 4 CPU cores (⭐ **Recommended**)
   - **Large VPS** - 8GB+ RAM, 8 CPU cores

2. **Budget Profile Selection**
   - **test** - $15/month budget
   - **prod** - $200/month budget
   - **unlimited** - $1000/month budget

3. **Port Configuration**
   - Nginx reverse proxy (enabled by default for security)
   - External ports (can use random high ports for security)
   - LiteLLM UI port (for admin access)

4. **Environment Configuration**
   - Generates `.env` file with all settings
   - Creates `config.yaml` for LiteLLM
   - Generates `docker-compose.override.yml` with your settings

### Generated Files {#generated-files}

After setup, the following files are created:

- **`.env`** - Environment variables (sensitive, permissions: 600)
  - Contains API keys, passwords, ports, and configuration
  - **⚠️ Never commit this file to git**
  
- **`config.yaml`** - LiteLLM configuration (permissions: 644)
  - Contains model configurations and provider settings
  - **⚠️ May contain sensitive data, do not commit to git**
  
- **`docker-compose.override.yml`** - Docker Compose overrides (permissions: 600)
  - Contains resource profiles, port mappings, and service configurations
  - **⚠️ Contains user-specific settings, do not commit to git**

All generated files are automatically added to `.gitignore` to prevent accidental commits.

### Troubleshooting Setup

**If setup fails:**

1. **Check Docker is running:**
   ```bash
   docker ps
   ```

2. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.8+
   ```

3. **Check file permissions:**
   ```bash
   ls -la setup.sh
   chmod +x setup.sh  # If needed
   ```

4. **View setup logs:**
   - Setup errors are displayed in the terminal
   - Check for specific error messages

See [Troubleshooting Guide](troubleshooting.md) for more help.

## Step 2: Start the System {#step-2-start-the-system}

After setup is complete, start the Docker containers:

### Linux/macOS

```bash
./start.sh
```

Or using the CLI:

```bash
./ai-gateway start
```

### Windows

```cmd
start.bat
```

### What Happens During Start

1. **Containers Start** - Docker Compose starts all services:
   - PostgreSQL (database)
   - LiteLLM (API proxy)
   - Open WebUI (web interface)
   - Nginx (reverse proxy, if enabled)

2. **Health Checks** - System waits for containers to become healthy

3. **Access Information** - URLs and access keys are displayed

4. **First Run Detection** - If this is the first run, Virtual Key setup instructions are shown

### Expected Output

After successful start, you'll see:

```
✅ Containers started and healthy!

🌐 Access URLs (local network):
  • Open WebUI: http://192.168.1.100:3000
  • LiteLLM API: http://192.168.1.100:3000/api/litellm/v1
    API Key: sk-xxxxxxxxxxxxx
  • LiteLLM UI: http://192.168.1.100:4000/ui

📊 Check status:
  docker compose ps

📝 View logs:
  docker compose logs -f
```

### Troubleshooting Start

**If containers won't start:**

1. **Check container status:**
   ```bash
   docker compose ps
   ```

2. **View container logs:**
   ```bash
   docker compose logs
   ```

3. **Check for port conflicts:**
   ```bash
   # Linux/macOS
   sudo lsof -i :3000
   sudo lsof -i :4000
   ```

4. **Stop and restart:**
   ```bash
   ./stop.sh
   ./start.sh
   ```

See [Troubleshooting Guide](troubleshooting.md#containers-wont-start) for detailed solutions.

## Step 3: Access and Configure {#step-3-access-and-configure}

After containers start, you need to:

1. Create a Virtual Key (required for Open WebUI)
2. Add providers (API keys for LLM services)
3. Add models (configure which models to use)

### Step 3.1: Create Virtual Key (Required) {#step-31-create-virtual-key-required}

**Virtual Key is required** for Open WebUI to work properly. It's more secure than using the Master Key directly.

#### Automatic Creation (Recommended)

On first run, the system will prompt you to create a Virtual Key. You can also run:

**Linux/macOS:**
```bash
./virtual-key.sh
```

**Windows:**
```cmd
virtual-key.bat
```

**What it does:**
- Creates a team "Open WebUI Team" in LiteLLM
- Creates a Virtual Key "Open WebUI Key" for the team
- Saves the Virtual Key to `.env` file
- Updates `FIRST_RUN` flag

**Prerequisites:**
- Containers must be running (`./start.sh`)
- LiteLLM must be accessible (may take 45+ seconds after container start)
- Master Key must be in `.env` file

#### Manual Creation

If automatic creation fails:

1. **Open LiteLLM Admin UI:**
   - URL: http://localhost:4000/ui (or your configured port)
   - Login with Master Key from `.env` file

2. **Create Team** (optional but recommended):
   - Go to **Teams/Users** section
   - Click "Create Team" or "Add Team"
   - Enter team name (e.g., "Open WebUI Team")
   - Save

3. **Create Virtual Key:**
   - In Teams section, select your team
   - Click "Create Key" or "Add Virtual Key"
   - Enter key name (e.g., "Open WebUI Key")
   - Configure permissions:
     - **Models**: Leave empty for all models, or select specific models
     - **Endpoints**: Leave default for full access
   - Save
   - **Copy the Virtual Key** (starts with `sk-`)

4. **Add to `.env` file:**
   ```bash
   # Edit .env file
   nano .env
   # Add line:
   VIRTUAL_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
   ```

📖 For detailed Virtual Key documentation, see [Virtual Key Configuration](configuration/virtual-key.md)

### Step 3.2: Add Providers {#step-32-add-providers}

Providers are the LLM services you want to use (Anthropic, OpenAI, Azure, etc.).

1. **Open LiteLLM Admin UI:**
   - URL: http://localhost:4000/ui (or your configured port)
   - Login with Master Key from `.env` file

2. **Go to Providers section:**
   - Click "Providers" or "API Keys" in the navigation

3. **Add Provider:**
   - Click "Add Provider" or "New Provider"
   - Select provider type (Anthropic, OpenAI, Azure, etc.)
   - Enter your API key
   - Configure settings (if needed):
     - **Anthropic**: Enter your API key, select tier if needed
     - **OpenAI**: Enter your API key
     - **Azure**: Enter API key, endpoint, and API version
     - **Google**: Enter API key
     - **Groq**: Enter API key
   - Save

**Common Providers:**

> 📚 **Full Provider List:** LiteLLM supports **100+ providers**. See [official documentation](https://docs.litellm.ai/docs/providers) for complete list and setup instructions.

**Most Popular Providers:**

- **Anthropic** - Claude models (Claude 3.5 Sonnet, Claude 3 Opus, etc.)
  - Get API key: https://console.anthropic.com/
  - ⚠️ Tier 1 has strict rate limits - Tier 2+ recommended
  - Environment variable: `ANTHROPIC_API_KEY`

- **OpenAI** - GPT models (GPT-4, GPT-3.5, etc.)
  - Get API key: https://platform.openai.com/api-keys
  - Environment variable: `OPENAI_API_KEY`

- **Azure OpenAI** - Azure-hosted OpenAI models
  - Requires Azure subscription and OpenAI resource
  - Environment variables: `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION`

- **Google AI Studio** - Gemini models (Gemini Pro, etc.)
  - Get API key: https://makersuite.google.com/app/apikey
  - Environment variable: `GEMINI_API_KEY` or `GOOGLE_API_KEY`

- **Groq** - Fast inference for open models
  - Get API key: https://console.groq.com/keys
  - Environment variable: `GROQ_API_KEY`

**Other Popular Providers:**

- **Mistral AI** - Mistral models
  - Environment variable: `MISTRAL_API_KEY`
  - Docs: https://docs.mistral.ai/api/

- **Deepseek** - Deepseek models
  - Environment variable: `DEEPSEEK_API_KEY`
  - Docs: https://deepseek.com/

- **Together AI** - Open models
  - Environment variable: `TOGETHER_API_KEY`
  - Docs: https://together.ai/

- **Perplexity AI** - Perplexity models
  - Environment variable: `PERPLEXITY_API_KEY`
  - Docs: https://www.perplexity.ai

- **xAI** - Grok models
  - Environment variable: `XAI_API_KEY`
  - Docs: https://docs.x.ai/docs

- **Cohere** - Cohere models
  - Environment variable: `COHERE_API_KEY`

- **Fireworks AI** - Fast inference
  - Environment variable: `FIREWORKS_API_KEY`
  - Docs: https://fireworks.ai/

- **OpenRouter** - Access to multiple models
  - Environment variable: `OPENROUTER_API_KEY`
  - Docs: https://openrouter.ai/

- **Ollama** - Local models
  - No API key required (local deployment)
  - Docs: https://ollama.ai/

- **LM Studio** - Local models
  - No API key required (local deployment)
  - Docs: https://lmstudio.ai/docs/basics/server

**Complete Provider List:**

See [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers) for:
- Full list of 100+ supported providers
- Provider-specific setup instructions
- Environment variable names
- Model ID formats
- Rate limits and pricing information

### Step 3.3: Add Models {#step-33-add-models}

After adding providers, add the models you want to use:

1. **Go to Models section:**
   - In LiteLLM Admin UI, click "Models" or "Model Config"

2. **Add Model:**
   - Click "Add Model" or "New Model"
   - Select provider
   - Enter model ID (e.g., `claude-sonnet-4-5` or `claude-3-5-sonnet` for Anthropic)
   - Configure settings (optional):
     - **Max tokens**: Maximum tokens per request
     - **Temperature**: Model temperature (0.0-2.0)
     - **Top P**: Top-p sampling parameter
   - Save

**Common Model IDs:**

> ⚠️ **CRITICAL:** Model IDs in LiteLLM may differ from provider's official names and can change over time. **Always verify actual model IDs** using one of these methods:
> 
> 1. **Via API:** `curl http://localhost:PORT/api/litellm/v1/models -H "Authorization: Bearer YOUR_KEY"`
> 2. **Via LiteLLM Admin UI:** Go to Models section to see configured models
> 3. **Via Provider Documentation:** Check [LiteLLM Providers Docs](https://docs.litellm.ai/docs/providers) for each provider's specific model IDs
>
> The examples below are **common patterns** but may not match your exact setup. Model IDs are configured in LiteLLM Admin UI and can be customized.

**Finding Model IDs for Each Provider:**

- **Anthropic (Claude):**
  - LiteLLM Docs: https://docs.litellm.ai/docs/providers/anthropic
  - Official Docs: https://docs.anthropic.com/claude/docs/models-overview
  - Common patterns: `claude-3-5-sonnet`, `claude-3-opus`, `claude-3-haiku`, `claude-sonnet-4-5`
  - ⚠️ **Note:** Model IDs may use different formats (e.g., `claude-sonnet-4-5` vs `claude-3-5-sonnet-20241022`)

- **OpenAI (GPT):**
  - LiteLLM Docs: https://docs.litellm.ai/docs/providers/openai
  - Official Docs: https://platform.openai.com/docs/models
  - Common patterns: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`
  - ⚠️ **Note:** Check LiteLLM docs for exact model ID format

- **Google AI Studio (Gemini):**
  - LiteLLM Docs: https://docs.litellm.ai/docs/providers/google_ai_studio
  - Official Docs: https://ai.google.dev/models/gemini
  - Common patterns: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-pro`, `gemini-pro-vision`
  - ⚠️ **Note:** Model IDs format may vary - check LiteLLM provider docs

- **Mistral AI:**
  - LiteLLM Docs: https://docs.litellm.ai/docs/providers/mistral
  - Official Docs: https://docs.mistral.ai/api/
  - Common patterns: `mistral-large`, `mistral-medium`, `mistral-small`
  - ⚠️ **Note:** Check LiteLLM docs for exact model IDs

- **Groq:**
  - LiteLLM Docs: https://docs.litellm.ai/docs/providers/groq
  - Official Docs: https://console.groq.com/docs/models
  - Common patterns: `llama-3.1-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`
  - ⚠️ **Note:** Model IDs format may differ - verify in LiteLLM docs

**For Other Providers:**

See [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers) for:
- Complete list of 100+ providers
- Provider-specific model ID formats
- Exact model names supported by LiteLLM
- Configuration examples

**Important Notes:**
- Model IDs in LiteLLM may differ from provider's official names
- Model IDs can be customized in LiteLLM Admin UI
- Models configured in LiteLLM Admin UI automatically appear in Open WebUI (no restart needed)
- **Always verify model IDs** using `/v1/models` API endpoint or LiteLLM Admin UI

## Step 4: First Use

After completing setup, you can start using AI Gateway:

### Access Open WebUI

1. **Open in browser:**
   - URL shown after startup (e.g., `http://localhost:3000`)
   - Or check access URLs with: `docker compose ps`

2. **First Login:**
   - Create an admin account (first user is admin)
   - Or login if account already exists

3. **Configure Connection:**
   - Go to **Settings → Connections**
   - Add connection:
     - **Name**: AI Gateway (or any name)
     - **API Base URL**: `http://litellm:4000/v1` (internal Docker network)
     - **API Key**: Virtual Key from `.env` file
   - Save

4. **Start Chatting:**
   - Select a model from the dropdown
   - Start a new conversation
   - Models configured in LiteLLM will appear automatically

### Use LiteLLM API

You can also use the API directly:

```bash
# List available models
curl http://localhost:3000/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY"

# Chat completion
curl http://localhost:3000/api/litellm/v1/chat/completions \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

📖 For API documentation, see [API for Agents](integrations/api-for-agents.md)

## Step 5: Optional Integrations

### Continue.dev Integration

Continue.dev is a VS Code extension for AI-powered coding assistance.

**Prerequisites:**
- ✅ AI Gateway running (`./start.sh`)
- ✅ Virtual Key created
- ✅ Providers and models configured

**Setup:**
```bash
./ai-gateway continue-dev
```

📖 For detailed instructions, see [Continue.dev Integration](integrations/continue-dev.md)

## Step 6: Daily Usage

### Starting the System

```bash
./start.sh  # Linux/macOS
start.bat    # Windows
```

### Stopping the System

```bash
./stop.sh  # Linux/macOS
stop.bat    # Windows
```

### Checking Status

```bash
# Container status
docker compose ps

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f litellm-proxy
docker compose logs -f open-webui
```

### Updating Configuration

To change settings (ports, resource profile, etc.):

```bash
./ai-gateway setup  # Re-run setup
```

Your existing configuration will be preserved (you can choose to reuse or recreate).

## If Dependencies Are Missing {#if-dependencies-are-missing}

### Installing Docker

**Linux (Ubuntu/Debian):**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

**macOS:**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Docker Compose is included

**Windows:**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Docker Compose is included

### Installing Python

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

**macOS:**
```bash
# Using Homebrew
brew install python3

# Or download from python.org
```

**Windows:**
- Download from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### Verifying Installation

After installation, verify:

```bash
# Check Docker
docker --version
docker compose version
docker ps

# Check Python
python3 --version
pip3 --version
```

## Troubleshooting

### Common Issues

**Containers won't start:**
- See [Troubleshooting Guide](troubleshooting.md#containers-wont-start)

**Port conflicts:**
- See [Troubleshooting Guide](troubleshooting.md#port-conflicts)

**Virtual Key creation fails:**
- See [Virtual Key Configuration](configuration/virtual-key.md#troubleshooting)

**Models not appearing in Open WebUI:**
- Verify Virtual Key is set in `.env`
- Check LiteLLM Admin UI - models should be visible
- Restart Open WebUI container: `docker compose restart open-webui`

**API calls failing:**
- Verify Virtual Key is correct
- Check API endpoint URL
- View LiteLLM logs: `docker compose logs litellm-proxy`

For more troubleshooting help, see [Troubleshooting Guide](troubleshooting.md)

## Next Steps

- **Configure SSL/HTTPS**: See [Nginx Configuration](nginx/README.md)
- **Set up Continue.dev**: See [Continue.dev Integration](integrations/continue-dev.md)
- **Understand architecture**: See [Project Architecture](architecture.md)
- **Configure security**: See [Security Guide](security.md)
- **API for agents**: See [API for Agents](integrations/api-for-agents.md)

## Getting Help

- **Documentation**: See [Documentation Index](README.md)
- **Troubleshooting**: See [Troubleshooting Guide](troubleshooting.md)
- **Issues**: Check GitHub issues or create a new one

---

**All configuration is done through LiteLLM Admin UI** (access URL shown after startup)
