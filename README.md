# AI Gateway

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**AI Gateway** - bundled solution for working with language models through a unified interface. Similar to LAMP/XAMPP stacks, AI Gateway bundles LiteLLM, Open WebUI, PostgreSQL, and Nginx into a single, easy-to-configure package.

**Version:** 0.0.2 (Prototype)

⚠️ **Note:** This is a **prototype** with known limitations. Not production-ready.

## Quick Start

### Requirements
- **Python**: 3.8+
- **Docker**: 20.10+ (Docker Compose v2)
- **RAM**: 3GB minimum (4GB recommended)
- **OS**: Linux (tested), macOS/Windows (experimental)

📖 For detailed requirements and resource profiles, see [System Requirements](docs/system-requirements.md)

### Setup (5 minutes)

```bash
# 1. Run setup
./setup.sh          # Linux/macOS
setup.bat           # Windows

# 2. Start containers
./start.sh          # Linux/macOS
start.bat           # Windows

# 3. Configure models
# Open LiteLLM Admin UI (URL shown after startup)
# Add providers and models through the UI
```

**That's it!** Models configured in LiteLLM Admin UI will automatically appear in Open WebUI.

## Basic Commands

```bash
# Setup (first time)
./setup.sh

# Start containers
./start.sh

# Stop containers
./stop.sh

# Check status
docker compose ps

# View logs
docker compose logs -f
```

## CLI Commands

```bash
./ai-gateway setup          # Run interactive setup
./ai-gateway start          # Start Docker containers
./ai-gateway stop           # Stop Docker containers
./ai-gateway continue-dev   # Generate Continue.dev configuration
./ai-gateway --help         # Show help
```

## Access URLs

After starting, you'll see:
- **Open WebUI**: http://localhost:PORT/ (web interface)
- **LiteLLM API**: http://localhost:PORT/api/litellm/v1/ (API endpoint)
- **LiteLLM Admin UI**: http://localhost:PORT/ui (admin interface)

Ports are configured during setup.

## Configuration

**All models are configured through LiteLLM Admin UI** - this is the only way to add and manage models.

1. Open LiteLLM Admin UI (URL shown after startup)
2. Add providers (Anthropic, OpenAI, etc.) with your API keys
3. Add models from your providers
4. Models will automatically appear in Open WebUI - no restart needed!

📖 For port configuration, resource profiles, and budget settings, see [Configuration Guide](docs/configuration.md)

## Documentation

📖 **Full documentation is available in [`docs/`](docs/):**

### Getting Started
- **[Getting Started Guide](docs/getting-started.md)** - Complete setup and launch guide (5 minutes)
- **[System Requirements](docs/system-requirements.md)** - Detailed requirements, resource profiles, and disk space
- **[Installation Guide](docs/installation.md)** - Detailed installation with system user setup

### Configuration & Administration
- **[Configuration Guide](docs/configuration.md)** - Port configuration, resource profiles, budget profiles
- **[Security Guide](docs/security.md)** - Security recommendations and SSL/HTTPS setup
- **[Systemd Service](docs/administration/systemd.md)** - Managing AI Gateway with systemd

### Integrations
- **[Continue.dev Integration](docs/integrations/continue-dev.md)** - VS Code extension integration
- **[GitHub Copilot Integration](docs/integrations/github-copilot.md)** - Experimental integration

### Infrastructure
- **[Nginx Configuration](docs/nginx/README.md)** - External nginx setup for SSL/HTTPS

### Troubleshooting & Reference
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Project Architecture](docs/architecture.md)** - Code structure and design principles

### Project Files
- [Contributing](CONTRIBUTING.md) - How to contribute to the project
- [Security Policy](SECURITY.md) - Security vulnerability reporting
- [Changelog](CHANGELOG.md) - List of changes and updates

## Features

- 🚀 **Quick Start** - setup in 5 minutes
- 🎯 **Unified Interface** - work with different LLM providers through one API
- 💰 **Budget Control** - built-in system for limits and cost tracking
- 🔒 **Security** - secure key and password generation
- 🐳 **Docker** - ready-to-use containers for all components
- 🌐 **Multi-provider** - support for Anthropic, OpenAI, Azure, Gemini, Groq and others
- 📊 **Admin UI** - convenient interface for managing models and settings
- 🎨 **Open WebUI** - modern web interface for chatting with models

## Known Limitations

- **Platform support**: Scripts tested on Linux. macOS and Windows support is experimental
- **Proxmox LXC**: Rootless Docker may not work in unprivileged LXC containers (use VM instead)
- **GitHub Copilot**: Requires complex setup (use Continue.dev instead)
- **Anthropic Tier 1**: Strict rate limits - Tier 2+ recommended

📖 For troubleshooting help, see [Troubleshooting Guide](docs/troubleshooting.md)

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [LiteLLM](https://github.com/BerriAI/litellm) - universal LLM proxy
- [Open WebUI](https://github.com/open-webui/open-webui) - web interface for LLM

---

**All configuration is done through LiteLLM Admin UI** (access URL shown after startup)
