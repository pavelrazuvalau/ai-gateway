# AI Gateway Documentation

Welcome to the AI Gateway documentation! This is the main source of information for using, configuring, and troubleshooting AI Gateway.

## 📚 Documentation Index

### Getting Started
- **[Getting Started Guide](getting-started.md)** - Complete setup and launch guide (5 minutes to get running)
- **[System Requirements](system-requirements.md)** - Detailed system requirements, resource profiles, and disk space requirements
- **[Installation Guide](installation.md)** - Detailed installation instructions with system user setup

### Configuration
- **[Configuration Guide](configuration.md)** - Port configuration, resource profiles, budget profiles, and memory settings
- **[Security Guide](security.md)** - Security recommendations, SSL/HTTPS setup, and best practices

### Integrations
- **[API for Agents](integrations/api-for-agents.md)** - Complete API documentation for AI agents and automated systems
- **[Continue.dev Integration](integrations/continue-dev.md)** - VS Code extension integration with automatic model discovery
- **[GitHub Copilot Integration](integrations/github-copilot.md)** - Experimental GitHub Copilot integration (use Continue.dev instead)

### Examples
- **[Examples Index](examples/README.md)** - Practical code examples and use cases
- **[Python Examples](examples/python-basic.md)** - Python integration examples
- **[JavaScript Examples](examples/javascript-basic.md)** - JavaScript/TypeScript examples
- **[Integration Examples](examples/integration-examples.md)** - Integration with popular frameworks
- **[Configuration Examples](examples/configuration-examples.md)** - Example configurations

### Infrastructure
- **[Nginx Configuration](nginx/)** - External nginx configuration examples for SSL/HTTPS
  - [External Nginx Example](nginx/external-nginx-example.conf) - Example configuration for SSL/HTTPS setup
  - [Nginx Setup Guide](nginx/README.md) - Detailed instructions for configuring external nginx with Let's Encrypt

### Troubleshooting
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

### Administration
- **[Systemd Service](administration/systemd.md)** - Managing AI Gateway with systemd

### Reference
- **[Project Concept](concept.md)** - Project concept, target audience, and use cases
- **[Project Architecture](architecture.md)** - Code structure and design principles
- **[Glossary](glossary.md)** - Definitions of key terms and concepts
- **[FAQ](FAQ.md)** - Frequently asked questions
- **[Contributing](../CONTRIBUTING.md)** - How to contribute to the project
- **[Security Policy](../SECURITY.md)** - Security policy
- **[Changelog](../CHANGELOG.md)** - List of changes and updates

## 🚀 Quick Start

If you're new to AI Gateway, start here:

1. **Check Requirements**: See [System Requirements](system-requirements.md) for minimum system requirements
2. **Run Setup**: Follow the [Getting Started Guide](getting-started.md) - takes about 5 minutes
3. **Configure Models**: Add providers and models through LiteLLM Admin UI (see [Getting Started - Step 3](getting-started.md#step-3-access-and-configure))
4. **Start Using**: Access Open WebUI and start chatting with models

## 📖 Main Documentation Files

These files are in the project root:

- **[README.md](../README.md)** - Quick overview and essential information for first-time users
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - How to contribute to the project
- **[SECURITY.md](../SECURITY.md)** - Security vulnerability reporting
- **[CHANGELOG.md](../CHANGELOG.md)** - List of changes and updates

## 💡 Common Tasks

- **First-time setup**: See [Getting Started Guide](getting-started.md)
- **Configure SSL/HTTPS**: See [Nginx Configuration](nginx/README.md)
- **Set up Continue.dev**: See [Continue.dev Integration](integrations/continue-dev.md)
- **Troubleshoot issues**: See [Troubleshooting Guide](troubleshooting.md)
- **Understand resource usage**: See [System Requirements](system-requirements.md)

## 🔍 Finding Information

- **New to AI Gateway?** → Start with [Getting Started Guide](getting-started.md)
- **Setting up for production?** → See [Security Guide](security.md) and [Nginx Configuration](nginx/README.md)
- **Having problems?** → Check [Troubleshooting Guide](troubleshooting.md)
- **Want to customize?** → See [Configuration Guide](configuration.md)
- **Need integration help?** → See [Integrations](integrations/)

## 📝 Documentation Structure

```
docs/
├── README.md                    # This file - main documentation index
├── getting-started.md          # Complete setup guide
├── installation.md             # Detailed installation guide
├── system-requirements.md      # System requirements and resource profiles
├── configuration.md            # Configuration options
├── security.md                 # Security guide
├── architecture.md             # Project architecture
├── troubleshooting.md          # Troubleshooting guide
├── FAQ.md                      # Frequently asked questions
├── glossary.md                 # Glossary of terms
├── administration/             # Administration guides
│   └── systemd.md             # Systemd service management
├── integrations/               # Integration guides
│   ├── api-for-agents.md     # API documentation for agents
│   ├── continue-dev.md        # Continue.dev integration
│   └── github-copilot.md      # GitHub Copilot integration
├── examples/                   # Code examples
│   ├── README.md              # Examples index
│   ├── python-basic.md        # Python examples
│   ├── javascript-basic.md    # JavaScript examples
│   ├── integration-examples.md # Framework integrations
│   └── configuration-examples.md # Configuration examples
└── nginx/                      # Nginx configuration examples
    ├── README.md              # Nginx setup guide
    └── external-nginx-example.conf  # Example configuration
```

---

**All configuration is done through LiteLLM Admin UI** (access URL shown after startup)
