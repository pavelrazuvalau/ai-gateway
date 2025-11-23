# AI Gateway

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**AI Gateway** - prototype bundled solution for working with language models through a unified interface. Similar to LAMP/XAMPP stacks, AI Gateway bundles LiteLLM, Open WebUI, PostgreSQL, and Nginx into a single, easy-to-configure package. All configuration is done through LiteLLM Admin UI.

⚠️ **Note:** This is a **prototype** with known limitations. Not production-ready.

**Known limitations:**
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
- **RAM**: 2GB minimum (4GB recommended)
- **CPU**: 2 cores minimum (4 cores recommended)
- **Disk**: 10GB minimum (see [Disk Space Requirements](#-disk-space-requirements) below for details)
- **OS**: Linux, macOS, or Windows (with WSL2)

### ⚠️ Proxmox LXC Containers

**Rootless Docker is not reliably supported in unprivileged Proxmox LXC containers** due to kernel-level restrictions on user namespaces. If you're using Proxmox, we recommend:

- **Use a full VM** instead of an LXC container for running AI Gateway
- **Or use a privileged LXC container** (less secure, but may work)

For more details, see the [Installation Guide](INSTALL.md#proxmox-lxc-containers).

### Recommended Requirements
- **RAM**: 4GB+ for production use
- **CPU**: 4+ cores for better performance
- **Network**: Stable internet connection for API calls to LLM providers

### Resource Profiles Explained
Each profile sets Docker container resource limits. The host system should have:
- **Small VPS**: 2GB RAM, 2 CPU cores (containers use ~1.6GB, ~1.9 CPU)
- **Medium VPS**: 4GB RAM, 4 CPU cores (containers use ~3.2GB, ~3.7 CPU)
- **Large VPS**: 8GB+ RAM, 8 CPU cores (containers use ~6.3GB, ~7.3 CPU)

**Note:** Resource limits are optimized based on PostgreSQL best practices and container memory constraints. PostgreSQL settings (`shared_buffers`, `effective_cache_size`, `work_mem`) are calculated based on container RAM limits, not host RAM.

### 💾 Disk Space Requirements

The system uses several Docker volumes for persistent data storage:

#### Base Storage (Required)
- **Docker Images**: ~3-4GB (PostgreSQL, LiteLLM, Open WebUI, Nginx, Certbot)
- **System & Logs**: ~500MB-1GB (Docker logs, system files, configs)
- **SSL Certificates**: ~10-50MB (if using HTTPS with Let's Encrypt)

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
3. **PostgreSQL maintenance**: Run `VACUUM` periodically to reclaim space
4. **Monitor usage**: Check volumes with:
   ```bash
   docker system df                    # Overall Docker disk usage
   docker volume ls                    # List all volumes
   docker volume inspect <volume_name> # Check specific volume size
   ```
5. **Backup strategy**: Plan for 2-3x storage for backups

## 🚀 Quick Start

### 1. Setup

```bash
# Linux/macOS
./setup.sh

# Windows
setup.bat
```

The setup script will ask for:
- Resource profile (Local/Small VPS/Medium VPS/Large VPS)
- Budget profile (test/prod/unlimited)
- Port settings

### 2. Start

```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

### 3. Configure Providers and Models

After startup, access URLs will be shown. Typically:
- **Open WebUI**: http://localhost:PORT (main port)
- **LiteLLM (API + UI)**: http://localhost:PORT (separate port)

In LiteLLM Admin UI:
- Add providers (Anthropic, Azure, OpenAI Compatible)
- Configure API keys
- Add models

### 4. Usage

Open **Open WebUI** from the main port shown after startup.

Create an account and start chatting with models.

## 📊 Resource Profiles

| Profile | RAM | CPU | Users | Description |
|---------|-----|-----|-------|-------------|
| **Local** | No limits | No limits | - | Local development |
| **Small VPS** | 2GB | 2 CPU | 1-2 | Budget option |
| **Medium VPS** | 4GB | 4 CPU | 3-5 | Recommended |
| **Large VPS** | 8GB+ | 8 CPU | 10+ | For teams |

**Note:** Resource limits are optimized for containers. Actual usage may vary based on workload. The system should have additional resources for the host OS and Docker overhead (~500MB-1GB RAM, ~0.5-1 CPU).

## 💰 Budget Profiles

| Profile | Total Budget | Description |
|---------|--------------|-------------|
| **test** | $15/month | Test environment |
| **prod** | $200/month | Production |
| **unlimited** | $1000/month | No limits |

You can change the profile:
- In `.env`: `BUDGET_PROFILE=test|prod|unlimited`
- When starting: `./start.sh prod`

## 🛠️ Commands

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

## 🔧 Port Configuration

By default:
- **Open WebUI**: 3000
- **LiteLLM API**: 4000
- **LiteLLM UI**: 4000/ui
- **PostgreSQL**: 5432 (internal)

Ports are configured when running `./ai-gateway setup` or `./setup.sh` or through `.env`.

## 🔒 Security

### For production:
- Change passwords in `.env` (POSTGRES_PASSWORD, UI_PASSWORD)
- Configure firewall
- Use reverse proxy with TLS (Nginx)
- Regularly update Docker images

## ❓ Troubleshooting

### Models don't appear in Open WebUI?
1. Add models through LiteLLM Admin UI (access URL shown after startup)
2. Restart: `docker compose restart litellm`

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

## 📚 Project Structure

```
.
├── ai-gateway            # Main CLI entry point (recommended)
├── setup.sh / setup.bat  # Setup wrapper (calls ./ai-gateway setup)
├── start.sh / start.bat  # Start system
├── stop.sh / stop.bat    # Stop system
├── docker-compose.yml    # Main Docker configuration
├── config.yaml           # LiteLLM configuration (auto-generated)
├── .env                  # Environment variables (auto-generated)
├── scripts/              # Utility scripts
│   └── setup_continue_dev.sh  # Continue.dev config generator
└── src/                  # Setup modules
    ├── budgets.py        # Budget profiles
    ├── config.py         # Resource profiles
    ├── config_generator.py
    ├── env_generator.py
    └── ...
```

## 🎯 What's Next?

1. Configure providers and models through Admin UI
2. Configure budgets and limits in Admin UI
3. Configure model fallback (in Admin UI)
4. Configure reverse proxy for production

## 🔌 Continue.dev Integration

AI Gateway includes a script to generate optimized Continue.dev configuration:

### Quick Setup

```bash
bash scripts/setup_continue_dev.sh
```

The script will:
- ✅ Fetch models dynamically from LiteLLM API
- ✅ Generate optimized configuration with proper roles (chat, edit, apply)
- ✅ Create system prompts in `.continue/prompts/` directory
- ✅ Configure AGENTS.md handling (optional)

### Generated Files

- `continue-dev-config-generated.yaml` - Continue.dev configuration (in `.gitignore`)
- `.continue/prompts/system-prompt.md` - System prompt for agents (in `.gitignore`)

**Note:** Generated files are excluded from git. Copy `continue-dev-config-generated.yaml` to your Continue.dev config directory (usually `~/.continue/`).

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

See `scripts/setup_continue_dev.sh` for detailed options and configuration.

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
