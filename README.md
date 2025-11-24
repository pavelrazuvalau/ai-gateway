# AI Gateway

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**AI Gateway** - prototype bundled solution for working with language models through a unified interface. Similar to LAMP/XAMPP stacks, AI Gateway bundles LiteLLM, Open WebUI, PostgreSQL, and Nginx into a single, easy-to-configure package. All configuration is done through LiteLLM Admin UI.

**Version:** 0.0.1 (Prototype)

⚠️ **Note:** This is a **prototype** with known limitations. Not production-ready.

**Known limitations:**
- **Platform support**: Scripts have been tested only on Linux. macOS and Windows support is experimental and not fully tested
- Rootless Docker may not work reliably in unprivileged Proxmox LXC containers (use full VM or privileged LXC)
- GitHub Copilot integration requires complex custom proxy setup (use Continue.dev instead)
- Anthropic API Tier 1 has strict rate limits (50k ITPM for Haiku, 30k for Sonnet/Opus) - Tier 2+ recommended for comfortable AI assistant usage
- Official documentation for some integrations (e.g., GitHub Copilot) may be incomplete

**Target audience:** Self-hosting enthusiasts who want more control and flexibility. Not for simple API usage.

## ✨ Features

- 🚀 **Quick Start** - setup in 5 minutes
- 🎯 **Unified Interface** - work with different LLM providers through one API
- 💰 **Budget Control** - built-in system for limits and cost tracking
- 🔒 **Security** - secure key and password generation
- 🐳 **Docker** - ready-to-use containers for all components
- 🌐 **Multi-provider** - support for Anthropic, OpenAI, Azure, Gemini, Groq and others
- 📊 **Admin UI** - convenient interface for managing models and settings
- 🎨 **Open WebUI** - modern web interface for chatting with models

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Docker**: 20.10 or higher (Docker Compose v2 recommended)
- **RAM**: 3GB minimum (4GB recommended) ⚠️ **Note**: Small VPS (2GB) profile uses ~2.8GB on typical Linux, or ~2.3GB with lightweight distro - see [Resource Profiles](#resource-profiles-explained) below
- **CPU**: 2 cores minimum (4 cores recommended)
- **Disk**: 10GB minimum (see [Disk Space Requirements](#-disk-space-requirements) below for details)
- **OS**: Linux (tested), macOS (experimental, not fully tested), Windows with WSL2 (experimental, not fully tested)

### ⚠️ Proxmox LXC Containers

**Rootless Docker is not reliably supported in unprivileged Proxmox LXC containers** due to kernel-level restrictions on user namespaces. If you're using Proxmox, we recommend:

- **Use a full VM** instead of an LXC container for running AI Gateway
- **Or use a privileged LXC container** (less secure, but may work)

For more details, see the [Installation Guide](INSTALL.md#proxmox-lxc-containers).

### Recommended Requirements
- **RAM**: 4GB+ for better performance
- **CPU**: 4+ cores for better performance
- **Network**: Stable internet connection for API calls to LLM providers

### 💡 Tips for Small VPS (2GB) Users

If you're using a Small VPS with 2GB RAM, consider using a **lightweight Linux distribution** to reduce system overhead:

- **Lightweight options**: Alpine Linux, Debian minimal, Ubuntu Server minimal
- **System overhead reduction**: From ~1.2GB (typical Linux) to ~600-800MB (lightweight distro)
- **Total usage with lightweight distro**: ~2.3GB (still tight but more feasible than ~2.8GB)
- **Note**: Even with a lightweight distro, 2GB is still tight. Medium VPS (4GB) is recommended for better performance and safety.

### Resource Profiles Explained
Each profile sets Docker container resource limits. **Memory usage is based on real measurements (2025-11-24)**. The host system should have:

- **Small VPS**: 2GB RAM, 2 CPU cores
  - ⚠️ **WARNING**: Actual usage is ~2.8GB on typical Linux distributions (exceeds 2GB by 40%)
  - Containers: ~1.6GB (LiteLLM: 780MB, Open WebUI: 602MB, PostgreSQL: 48MB, Nginx: 6MB)
  - System overhead: ~1.2GB (typical Linux) or ~600-800MB (lightweight distro)
  - **Recommendations**:
    - **Option 1**: Use Medium VPS (4GB) for safety ⭐ **Recommended**
    - **Option 2**: Use lightweight Linux distribution (Alpine, Debian minimal, Ubuntu Server minimal) to reduce system overhead to ~600-800MB, bringing total to ~2.3GB (still tight but more feasible)
- **Medium VPS**: 4GB RAM, 4 CPU cores ⭐ **Recommended**
  - Actual usage: ~3.3GB (safe with ~700MB buffer)
  - Containers: ~2.1GB (LiteLLM: 1.24GB with 2 workers, Open WebUI: 602MB, PostgreSQL: 48MB, Nginx: 6MB)
  - System overhead: ~1.2GB
- **Large VPS**: 8GB+ RAM, 8 CPU cores
  - Actual usage: ~5.1GB (leaves ~3GB buffer)
  - Containers: ~3.9GB (LiteLLM: 3.08GB with 6 workers, Open WebUI: 602MB, PostgreSQL: 48MB, Nginx: 6MB)
  - System overhead: ~1.2GB

**Memory Details:**
- Each LiteLLM worker uses ~460MB RAM (measured, not estimated)
- LiteLLM base process: ~320MB
- Open WebUI: ~602MB
- PostgreSQL: ~48MB (idle, can grow with usage)
- Nginx: ~6MB
- System overhead: 
  - ~1.2GB on typical Linux distributions (Ubuntu, Debian with desktop, Fedora)
  - ~600-800MB on lightweight distributions (Alpine, Debian minimal, Ubuntu Server minimal)
  - Includes OS, Docker daemons, and other system services

**Note:** Resource limits are optimized based on PostgreSQL best practices and container memory constraints. PostgreSQL settings (`shared_buffers`, `effective_cache_size`, `work_mem`) are calculated based on container RAM limits, not host RAM. Memory limits are configured in `docker-compose.yml` to prevent unbounded growth.

### 💾 Disk Space Requirements

The system uses several Docker volumes for persistent data storage:

#### Base Storage (Required)
- **Docker Images**: ~3-4GB (PostgreSQL, LiteLLM, Open WebUI, Nginx)
- **System & Logs**: ~500MB-1GB (Docker logs, system files, configs)

#### Persistent Data Volumes

| Volume | What's Stored | Small VPS | Medium VPS | Large VPS |
|--------|---------------|-----------|------------|-----------|
| **PostgreSQL** | Model configs, usage logs, metadata | 100-500MB | 500MB-2GB | 2-10GB |
| **Open WebUI** | Chat history, user data, files | 200MB-1GB | 1-5GB | 5-20GB+ |

#### Storage Recommendations by Profile

**Small VPS (1-2 users, occasional use):**
- **Minimum**: 10GB
- **Recommended**: 15-20GB
- **Breakdown**:
  - Docker images: 4GB
  - PostgreSQL: 500MB-1GB (few models, minimal logging)
  - Open WebUI: 500MB-2GB (limited chat history)
  - Logs & system: 1GB
  - Buffer: 3-5GB

**Medium VPS (3-5 users, regular use):**
- **Minimum**: 20GB
- **Recommended**: 30-40GB
- **Breakdown**:
  - Docker images: 4GB
  - PostgreSQL: 1-3GB (multiple models, moderate logging)
  - Open WebUI: 2-8GB (active chat history, some file uploads)
  - Logs & system: 2GB
  - Buffer: 5-10GB

**Large VPS (10+ users, active use):**
- **Minimum**: 50GB
- **Recommended**: 100GB+
- **Breakdown**:
  - Docker images: 4GB
  - PostgreSQL: 5-15GB (many models, detailed logging, analytics)
  - Open WebUI: 10-50GB+ (extensive chat history, file uploads, RAG data)
  - Logs & system: 5GB
  - Buffer: 20GB+

#### Growth Factors

Storage usage grows based on:
- **Number of users**: Each user's chat history and files
- **Chat activity**: More conversations = more storage
- **File uploads**: RAG documents, images, attachments
- **Model configurations**: More models = larger PostgreSQL database
- **Logging level**: Detailed logging increases PostgreSQL size
- **Retention period**: How long chat history is kept

#### Storage Optimization Tips

1. **Regular cleanup**: Periodically remove old chat history in Open WebUI
2. **Log rotation**: Already configured (max 3-5 files per service)
3. **Monitor usage**: Check volumes with:
   ```bash
   docker system df                    # Overall Docker disk usage
   docker volume ls                    # List all volumes
   docker volume inspect <volume_name> # Check specific volume size
   ```

## 🚀 Quick Start

This guide will walk you through the complete setup and launch process. The entire process takes about 5 minutes.

### Step 1: Run Setup Script

The setup script (`setup.sh` or `setup.bat`) performs automatic dependency checks and interactive configuration:

```bash
# Linux/macOS
./setup.sh

# Windows
setup.bat
```

#### What the Setup Script Does:

1. **Dependency Checks** (automatic):
   - ✅ Checks if Python 3.8+ is installed (with installation instructions if missing)
   - ✅ Checks if Docker is installed (with installation instructions if missing)
   - ✅ Checks if Docker Compose is available
   - ✅ Verifies Docker daemon is running (with start instructions if not)

2. **Environment Setup** (automatic):
   - Creates Python virtual environment (`venv/`)
   - Installs required Python packages from `requirements.txt`

3. **Interactive Configuration** (you'll be asked):
   - **Resource Profile** - Choose based on your system:
     - `[1] Desktop` - Local development (no limits)
     - `[2] Small VPS` - 2GB RAM, 2 CPU cores (1-2 users) ⚠️ **Warning**: Actual usage ~2.8GB - consider Medium VPS
     - `[3] Medium VPS` - 4GB RAM, 4 CPU cores (3-5 users) ⭐ **Recommended** - Actual usage ~3.3GB
     - `[4] Large VPS` - 8GB+ RAM, 8 CPU cores (10+ users) - Actual usage ~5.1GB
     - `[5] Don't configure workers` - Use LiteLLM defaults
   
   - **Budget Profile** - Spending limits for API calls:
     - `[1] Test` - $15/month (recommended for testing)
     - `[2] Prod` - $200/month
     - `[3] Unlimited` - $1000/month (use with caution!)
   
   - **Port Configuration**:
     - **Nginx Reverse Proxy** (enabled by default, recommended):
       - Exposes only one external port for enhanced security
       - Open WebUI and LiteLLM API accessible through single port
       - All other services (PostgreSQL, LiteLLM UI) remain internal
       - You can disable it if you prefer separate ports for each service
     - Port selection: default ports, manual configuration, or random high ports
   
   - **Systemd Service** (Linux only, optional):
     - Install as systemd user service for auto-start on boot

4. **File Generation** (automatic):
   - Creates `.env` file with generated passwords and keys
   - Creates `config.yaml` with LiteLLM configuration
   - Creates `docker-compose.override.yml` with resource limits
   - Generates Nginx configuration files

5. **Optional: Continue.dev Setup** (recommended to skip during initial setup):
   - After main setup, you'll be asked if you want to configure Continue.dev (VS Code extension)
   - ⚠️ **Important**: Continue.dev setup requires models to be already configured in LiteLLM Admin UI
   - **Recommended**: Skip this during initial setup, configure later after adding models (see [Continue.dev Integration](#-continue.dev-integration) section)
   - The script fetches models from LiteLLM API, so models must exist first

#### If Dependencies Are Missing:

The setup script will show clear instructions for your platform:

**Python not found:**
- Fedora/RHEL: `sudo dnf install python3 python3-pip python3-venv`
- Ubuntu/Debian: `sudo apt install python3 python3-pip python3-venv`
- Arch: `sudo pacman -S python python-pip`
- macOS: `brew install python@3.11`

**Docker not found:**
- Follow official Docker installation guide for your platform
- Linux: Usually `sudo dnf install docker docker-compose` or `sudo apt install docker.io docker-compose`

**Docker daemon not running:**
- Linux (rootless): `systemctl --user start docker`
- Linux (system-wide): `sudo systemctl start docker`
- macOS: Start Docker Desktop from Applications
- Windows: Start Docker Desktop from Start menu

### Step 2: Start the System

After setup completes, you can start the system:

```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

#### What the Start Script Does:

1. **Pre-flight Checks**:
   - Verifies `.env` file exists (if not, offers to run setup)
   - Checks Docker daemon is running (with start instructions if not)
   - Validates PostgreSQL configuration
   - Checks budget profile settings

2. **Container Startup**:
   - Starts all Docker containers (PostgreSQL, LiteLLM, Open WebUI, Nginx)
   - Waits for health checks to pass (may take 1-2 minutes on first run)
   - Shows container status and access URLs

3. **First Run Instructions**:
   - If this is the first run, shows instructions for setting up Virtual Keys in LiteLLM Admin UI

#### Alternative: Start from Setup

You can also start immediately after setup completes - the setup script will ask if you want to start containers automatically.

### Step 3: Access and Configure

After containers start, you'll see access URLs like:

```
✅ Containers are running!

🌐 Access URLs:
   Open WebUI:    http://localhost:3000
   LiteLLM API:   http://localhost:4000
   LiteLLM Admin: http://localhost:4000/ui
```

#### Configure Providers and Models:

**All models are configured through LiteLLM Admin UI** - this is the only way to add and manage models.

1. **Open LiteLLM Admin UI** (http://localhost:4000/ui)
   - Use the master key from `.env` file (starts with `sk-`)

2. **Add Providers**:
   - Click "Add Provider" or "Add Key"
   - Select provider type (Anthropic, OpenAI, Azure, etc.)
   - Enter your API key
   - Save

3. **Add Models** (in LiteLLM Admin UI):
   - Go to "Models" section
   - Click "Add Model"
   - Select from available models for your providers
   - Configure model settings (temperature, max tokens, etc.)
   - Save

4. **Set Budgets** (optional, in LiteLLM Admin UI):
   - Configure spending limits per model or provider
   - Set up alerts for budget thresholds

**Important:** Once models are properly configured in LiteLLM Admin UI, they will automatically appear in Open WebUI - no restart needed!

### Step 4: Start Using

1. **Open WebUI** (http://localhost:3000):
   - Create your first account (first user becomes admin)
   - **Models configured in LiteLLM Admin UI will appear automatically** - no restart needed!
   - Start chatting with models

2. **API Access** (http://localhost:4000):
   - Use LiteLLM API endpoint for programmatic access
   - API key is the master key from `.env` file

### Quick Reference: Common Workflows

**First-time setup:**
```bash
./setup.sh          # Run setup (checks dependencies, configures everything)
./start.sh           # Start containers
# Then configure providers/models via LiteLLM Admin UI
# After models are configured, you can run: ./ai-gateway continue-dev
```

**Daily usage:**
```bash
./start.sh           # Start containers
# Use Open WebUI or API
./stop.sh            # Stop containers when done
```

**Update configuration:**
```bash
./setup.sh           # Re-run setup (will detect existing .env and ask to update)
```

**Check status:**
```bash
docker compose ps    # Show container status
docker compose logs # Show logs
```

## 📊 Resource Profiles

| Profile | RAM | CPU | Users | Description |
|---------|-----|-----|-------|-------------|
| **Local** | No limits | No limits | - | Local development |
| **Small VPS** | 2GB | 2 CPU | 1-2 | ⚠️ **Warning**: Actual usage ~2.8GB (exceeds 2GB) |
| **Medium VPS** | 4GB | 4 CPU | 3-5 | ⭐ **Recommended** - Actual usage ~3.3GB |
| **Large VPS** | 8GB+ | 8 CPU | 10+ | For teams - Actual usage ~5.1GB |

**Note:** Memory usage is based on real measurements (2025-11-24). Each LiteLLM worker uses ~460MB RAM. The system includes memory limits in `docker-compose.yml` to prevent unbounded growth. See [Resource Profiles Explained](#resource-profiles-explained) above for detailed breakdown.

## 💰 Budget Profiles

| Profile | Total Budget | Description |
|---------|--------------|-------------|
| **test** | $15/month | Test environment |
| **prod** | $200/month | Regular use |
| **unlimited** | $1000/month | No limits |

You can change the profile:
- In `.env`: `BUDGET_PROFILE=test|prod|unlimited`
- When starting: `./start.sh prod`

## 🛠️ Commands

### CLI Commands (Recommended)

All commands are available via the unified CLI:

```bash
./ai-gateway setup          # Run interactive setup
./ai-gateway start          # Start Docker containers
./ai-gateway stop           # Stop Docker containers
./ai-gateway continue-dev   # Generate Continue.dev configuration
./ai-gateway --help         # Show help message
```

**Architecture**: The CLI (`./ai-gateway`) is a Python entry point that calls application services. Bash scripts are wrappers that set up the Python environment and call the CLI.

### Manual Management (Scripts)

```bash
# Start
./start.sh          # Linux/macOS
start.bat           # Windows

# Stop
./stop.sh           # Linux/macOS
stop.bat            # Windows

# Check status
docker compose ps

# Logs
docker compose logs -f

# Restart
docker compose restart
```

### Systemd Service (Linux Only, Recommended)

During setup, you can optionally install AI Gateway as a systemd user service for automatic startup and background operation:

```bash
# Service management
systemctl --user start ai-gateway.service      # Start
systemctl --user stop ai-gateway.service       # Stop
systemctl --user restart ai-gateway.service    # Restart
systemctl --user status ai-gateway.service     # Status

# View logs
journalctl --user -u ai-gateway.service -f     # Follow logs
journalctl --user -u ai-gateway.service -n 50  # Last 50 lines

# Enable/disable autostart
systemctl --user enable ai-gateway.service     # Enable (done automatically during setup)
systemctl --user disable ai-gateway.service    # Disable
```

**Benefits:**
- ✅ Automatic startup on system boot
- ✅ Runs in background even after SSH logout
- ✅ Automatic restart on failures
- ✅ Centralized logging via journalctl

See [SYSTEMD.md](SYSTEMD.md) for detailed documentation.

## 💾 Memory Configuration

### Memory Limits

Memory limits are configured in `docker-compose.yml` to prevent containers from consuming unbounded memory. These limits are based on real measurements and allow for growth while preventing OOM (Out of Memory) kills.

**Current Memory Limits:**
- **litellm**: 1.5G limit, 1.2G reservation
  - Current usage: ~1.177 GiB (with 2 workers)
  - Allows growth for additional workers or increased load
- **open-webui**: 800M limit, 600M reservation
  - Current usage: ~602 MB
  - Allows growth for chat history and file uploads
- **postgres**: 200M limit, 100M reservation
  - Current usage: ~48 MB (idle)
  - Allows growth for database size and query cache
- **nginx**: 100M limit, 50M reservation
  - Current usage: ~6 MB
  - Allows growth for high traffic

**To adjust memory limits:**

Edit `docker-compose.yml` and modify the `deploy.resources.limits.memory` values:

```yaml
services:
  litellm:
    deploy:
      resources:
        limits:
          memory: 1.5G  # Adjust as needed
        reservations:
          memory: 1.2G  # Adjust as needed
```

**After changing limits:**
```bash
docker compose down
docker compose up -d
```

**Note:** If you increase limits significantly, ensure your host system has enough RAM. See [Resource Profiles Explained](#resource-profiles-explained) for total system requirements.

## 🔧 Port Configuration

### Default Configuration (with Nginx - Enabled by Default)

**During setup, Nginx reverse proxy is enabled by default** (you can disable it if needed). This provides enhanced security by exposing only one external port:

- **Single External Port** (via Nginx):
  - **Open WebUI**: Available at root path `/` (e.g., `http://localhost:PORT/`)
  - **LiteLLM API**: Available at `/api/litellm/v1/*` (e.g., `http://localhost:PORT/api/litellm/v1/chat/completions`)
  - **All other services**: Closed to external access (PostgreSQL, LiteLLM UI remain internal)

- **LiteLLM UI**: Still accessible on separate port for local network configuration (optional)

**Ports are configured when running `./ai-gateway setup` or `./setup.sh`** - Nginx reverse proxy is enabled by default (press Enter to accept, or type 'n' to disable).

### Alternative Configuration (without Nginx)

If you disable Nginx during setup, services will be exposed on separate ports:
- **Open WebUI**: 3000
- **LiteLLM API**: 4000
- **LiteLLM UI**: 4000/ui
- **PostgreSQL**: 5432 (internal only)

## 🔒 Security

### Basic Security Recommendations:

1. **Change default passwords**:
   - Update passwords in `.env` (POSTGRES_PASSWORD, UI_PASSWORD)
   - The master key (LITELLM_MASTER_KEY) is auto-generated, but you can change it

2. **Use Nginx Reverse Proxy** (enabled by default):
   - Nginx is enabled by default during setup for enhanced security
   - Exposes only one external port
   - Open WebUI and LiteLLM API accessible through single port
   - PostgreSQL and internal services remain closed to external access

3. **Keep software updated**:
   - Update Docker images: `docker compose pull`
   - Update Python dependencies: `pip install -U -r requirements.txt`

**Note:** This is a prototype version. For production use, additional security measures should be implemented (firewall, TLS/HTTPS, etc.).

## ❓ Troubleshooting

### Models don't appear in Open WebUI?
1. Make sure models are configured in LiteLLM Admin UI (http://localhost:4000/ui)
2. Models should appear automatically - no restart needed
3. If models still don't appear, check:
   - Models are properly saved in LiteLLM Admin UI
   - Providers have valid API keys
   - Try refreshing Open WebUI page
   - As last resort: `docker compose restart litellm`

### "master key invalid" error?
Make sure `LITELLM_MASTER_KEY` in `.env` starts with `sk-`

### Containers won't start?
```bash
# Check logs
docker compose logs

# Full restart
docker compose down
docker compose up -d
```

### PostgreSQL won't connect?
If password was changed, remove the volume:
```bash
docker compose down -v
docker compose up -d
```

### Memory Issues / Out of Memory (OOM) Errors?

**Check current memory usage:**
```bash
# Check container memory usage
docker stats --no-stream

# Check system memory
free -h

# Check for OOM kills
dmesg | grep -i "out of memory"
journalctl -k | grep -i "out of memory"
```

**Memory limits are configured** in `docker-compose.yml` to prevent unbounded growth:
- `litellm`: 1.5G limit (current: ~1.177 GiB with 2 workers)
- `open-webui`: 800M limit (current: ~602 MB)
- `postgres`: 200M limit (current: ~48 MB)
- `nginx`: 100M limit (current: ~6 MB)

**If containers are being killed due to memory limits:**

1. **Check actual usage**:
   ```bash
   docker stats --no-stream
   ```

2. **If limits are too low**, edit `docker-compose.yml` and increase the `deploy.resources.limits.memory` values

3. **If system is running out of memory**:
   - Consider upgrading to a larger VPS (Medium VPS recommended for 4GB systems)
   - Reduce number of LiteLLM workers (edit `docker-compose.override.yml`, change `--num_workers`)
   - Monitor with: `docker stats` and `free -h`

4. **For Small VPS (2GB) users**:
   - ⚠️ Small VPS profile actually uses ~2.8GB on typical Linux distributions, exceeding 2GB by 40%
   - **Recommendations**:
     - **Best option**: Upgrade to Medium VPS (4GB) for safety ⭐
     - **Alternative 1**: Use lightweight Linux distribution (Alpine, Debian minimal, Ubuntu Server minimal) to reduce system overhead from ~1.2GB to ~600-800MB, bringing total to ~2.3GB (still tight but more feasible)
     - **Alternative 2**: If you must use 2GB with typical Linux, consider reducing to 1 worker (but performance will be limited)

**Memory usage details:**
- Each LiteLLM worker uses ~460MB RAM (measured)
- LiteLLM base process: ~320MB
- System overhead: ~1.2GB (OS, Docker daemons)
- See [Resource Profiles Explained](#resource-profiles-explained) for full breakdown

## 📚 Project Structure

```
.
├── ai-gateway            # Main CLI entry point (Python)
├── setup.sh / setup.bat  # Setup wrapper (calls ./ai-gateway setup)
├── start.sh / start.bat  # Start wrapper (calls ./ai-gateway start)
├── stop.sh / stop.bat    # Stop system
├── continue-dev.sh # Continue.dev wrapper (calls ./ai-gateway continue-dev)
├── docker-compose.yml    # Main Docker configuration
├── config.yaml           # LiteLLM configuration (auto-generated)
├── .env                  # Environment variables (auto-generated)
└── src/                  # Python source code (layered architecture)
    ├── core/             # Domain logic and business rules
    ├── infrastructure/   # Infrastructure layer (files, Docker, logging)
    ├── application/      # Application layer (business logic)
    │   ├── setup_service.py      # Setup service
    │   ├── start_service.py      # Start service
    │   └── continue_dev_service.py  # Continue.dev service
    ├── budgets.py        # Budget profiles
    ├── config.py         # Resource profiles
    ├── config_generator.py
    ├── env_generator.py
    └── ...
```

**Architecture**: Bash scripts are **wrappers** that set up Python virtual environment and call Python modules. All business logic is in Python following layered architecture (Core → Infrastructure → Application).

## 🎯 What's Next?

**All configuration is done through LiteLLM Admin UI** (http://localhost:4000/ui):

1. Configure providers and models through LiteLLM Admin UI
2. Configure budgets and limits in LiteLLM Admin UI
3. Configure model fallback in LiteLLM Admin UI
4. Models will automatically appear in Open WebUI once configured
5. Nginx reverse proxy is enabled by default during setup (provides single port access)

## 🔌 Continue.dev Integration

AI Gateway includes a Python service to generate optimized Continue.dev configuration for VS Code extension. The service is accessible via CLI command or bash wrapper script.

### ⚠️ Important Prerequisites

**Before running the Continue.dev setup script, you MUST:**
1. ✅ Have AI Gateway running (`./start.sh`)
2. ✅ Have configured providers in LiteLLM Admin UI
3. ✅ Have added models in LiteLLM Admin UI
4. ✅ Have created a Virtual Key in LiteLLM Admin UI (required for API access)

**Why?** The script fetches models dynamically from LiteLLM API (`/v1/models` endpoint). If models are not configured yet, the script won't be able to generate the configuration automatically.

### Quick Setup

**Step 1:** Make sure models are configured (see [Step 3: Access and Configure](#step-3-access-and-configure) above)

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

### Generated Files

- `continue-dev-config-generated.yaml` - Continue.dev configuration (in `.gitignore`)
- `.continue/prompts/system-prompt.md` - System prompt for agents (in `.gitignore`)

**Note:** Generated files are excluded from git. Copy `continue-dev-config-generated.yaml` to your Continue.dev config directory (usually `~/.continue/`).

### When to Run the Script

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

### Features

- **Automatic model discovery** - No need to manually configure models
- **Tier-based configuration** - Optimized system prompts and context length based on Anthropic API tier (1-4)
- **Optimized for token usage** - Tier-specific prompts (Tier 1: strict control, Tier 2+: flexible approach)
- **AGENTS.md support** - Optional integration with project documentation
- **Context providers management** - Automatically disabled for Tier 1, enabled for Tier 2+ to prevent rate limit issues

### Anthropic API Tier Selection

The script will prompt you to select your Anthropic API tier (1-4) based on your account limits:
- **Tier 1**: Strict control, limited context providers (50k ITPM for Haiku, 30k for Sonnet/Opus)
- **Tier 2+**: Flexible approach, all context providers enabled (500k-4M ITPM)

**Architecture**: The bash script `continue-dev.sh` is a wrapper that sets up Python virtual environment and calls the Python service (`ContinueDevService` in `src/application/continue_dev_service.py`). All business logic is in Python.

## 🔌 GitHub Copilot Integration

⚠️ **Why the official documentation doesn't work:** The official LiteLLM documentation for GitHub Copilot integration ([link](https://docs.litellm.ai/docs/tutorials/github_copilot_integration)) is incomplete. GitHub Copilot requires:
- Special `/v1/engines` endpoint for model discovery
- Complex authentication with temporary tokens (in headers or URL-encoded query parameters)
- Automatic URL rewriting (`/v1/engines/...` → `/v1/chat/completions`)
- Custom proxy service to handle these requirements

**Status:** Experimental. Requires custom Python proxy service and Nginx routing. Implementation involves:
- Custom Python proxy service to handle `/v1/engines` endpoint
- Nginx routing with token validation (supports both header and URL-encoded query parameters)
- Automatic URL rewriting from `/v1/engines/...` to `/v1/chat/completions`
- Model creation scripts for Copilot compatibility

💡 **Recommended alternative:** Use [Continue.dev](https://continue.dev/) for VS Code instead. It's an open-source AI coding assistant that works seamlessly with AI Gateway through the [Continue.dev Integration](#-continue.dev-integration) script above. Continue.dev provides better control, customization, and doesn't require complex proxy setups.

## 📖 Documentation

- [Project Architecture](ARCHITECTURE.md) - code structure description
- [Installation Guide](INSTALL.md) - detailed installation instructions
- [Systemd Service](SYSTEMD.md) - systemd service management
- [Contributing](CONTRIBUTING.md) - how to contribute to the project
- [Security Policy](SECURITY.md) - security policy
- [Changelog](CHANGELOG.md) - list of changes and updates

## 🤝 Contributing

We welcome any contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a Pull Request.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [LiteLLM](https://github.com/BerriAI/litellm) - universal LLM proxy
- [Open WebUI](https://github.com/open-webui/open-webui) - web interface for LLM

---

**All configuration is done through LiteLLM Admin UI** (access URL shown after startup)
