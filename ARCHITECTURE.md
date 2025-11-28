# AI Gateway Architecture

**AI Gateway** is a bundled solution (LiteLLM + Open WebUI + PostgreSQL + Nginx) for working with language models, similar to LAMP/XAMPP stacks.

> 📖 **Full documentation**: See [docs/architecture.md](docs/architecture.md) for complete architecture documentation with diagrams and detailed explanations.

## Overview

The project uses a **layered architecture** with clear separation of concerns:

- **Python modules**: Layered architecture for business logic and configuration
- **Bash scripts**: Wrapper scripts that set up environment and call Python modules
- **Docker configuration**: Container orchestration

**Key Principle**: Bash scripts are **wrappers only**. They:
1. Set up Python virtual environment (using `venv.sh`)
2. Activate virtual environment
3. Call Python CLI (`./ai-gateway <command>`) which executes Python services
4. All business logic is in Python modules following layered architecture

## Architecture Layers

- **`core/`**: Domain logic, exceptions, configuration classes
- **`infrastructure/`**: External dependencies (files, Docker, logging, security)
- **`application/`**: Business logic and use cases (services)

## Key Components

- **Bash wrappers**: `start.sh`, `stop.sh`, `setup.sh`, `continue-dev.sh`, `venv.sh`
- **Python CLI**: `./ai-gateway` entry point with commands
- **Services**: `StartService`, `SetupService`, `ContinueDevService`
- **Shared modules**: `script_init.sh`, `check_dependencies.py`

## Design Principles

1. **Layer Separation**: Clear boundaries between core, infrastructure, and application
2. **Dependency Inversion**: Infrastructure depends on core, not vice versa
3. **Repository Pattern**: File operations encapsulated in `FileRepository`
4. **Centralized Configuration**: All config via `AppConfig` from `core.config`
5. **Simplicity First**: No automatic root operations, no automatic file copying

For detailed information, examples, and diagrams, see [docs/architecture.md](docs/architecture.md).
