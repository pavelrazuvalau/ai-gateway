# AI Gateway Architecture

**AI Gateway** is a bundled solution (LiteLLM + Open WebUI + PostgreSQL + Nginx) for working with language models, similar to LAMP/XAMPP stacks. This document describes the project's code structure and architecture.

## Overview

The project uses a layered architecture (Layered Architecture) with clear separation of concerns. The codebase consists of:

- **Python modules**: Layered architecture for business logic and configuration
- **Bash scripts**: Wrapper scripts that set up environment and call Python modules
- **Docker configuration**: Container orchestration

**Key Principle**: Bash scripts are **wrappers only**. They:
1. Set up Python virtual environment (using `venv.sh`)
2. Activate virtual environment
3. Call Python CLI (`./ai-gateway <command>`) which executes Python services
4. All business logic is in Python modules following layered architecture

## Project Structure

```text
ai-gateway/
├── src/                    # Python source code (layered architecture)
│   ├── core/               # Domain logic and business rules
│   ├── infrastructure/     # Infrastructure layer
│   ├── application/        # Application layer
│   ├── script_init.py      # Python script initialization
│   ├── script_init_bash.sh # Bash script initialization (shared module)
│   └── check_dependencies.py # Unified dependency checking
├── start.sh                # Main startup script (user-only, no root)
├── stop.sh                 # Stop containers script
├── setup.sh                # Setup wrapper (calls venv.sh + setup module)
├── venv.sh                 # Virtual environment setup
├── setup.py                 # Python setup script
├── user.sh                 # Optional: System user setup automation
├── update.sh               # Optional: File update automation
├── docker-compose.yml      # Docker Compose configuration
└── [config files]          # .env, config.yaml, etc.
```

## Python Package Structure

```text
src/
├── core/              # Domain logic and business rules
│   ├── exceptions.py  # Custom exceptions
│   └── config.py      # Configuration classes
├── infrastructure/    # Infrastructure layer
│   ├── logger.py      # Structured logging
│   ├── file_repository.py  # File system operations (Repository pattern)
│   ├── docker_client.py    # Docker operations
│   └── security.py         # Password and key generation
├── application/       # Application layer (business logic)
│   ├── services.py    # Application services
│   ├── setup_service.py    # Setup service
│   ├── start_service.py    # Start service
│   └── continue_dev_service.py  # Continue.dev configuration service
└── [legacy modules]   # Old modules (for backward compatibility)
```

## Bash Scripts Architecture

**Important**: Bash scripts are **wrappers** that set up the environment and call Python modules. All business logic is in Python.

### Core Scripts (Required)

- **`start.sh`**: Main entry point
  - Blocks root execution (must run as regular user)
  - Works from current directory (no automatic file copying)
  - Ensures virtual environment
  - Checks dependencies (Python + Bash fallback)
  - Calls `./ai-gateway start` (Python module: `StartService`)

- **`stop.sh`**: Stop containers
  - Checks dependencies
  - Stops Docker Compose services

- **`setup.sh`**: Setup wrapper
  - Calls `venv.sh` to avoid code duplication
  - Calls `./ai-gateway setup` (Python module: `SetupService`)
  - Optionally offers Continue.dev setup

- **`continue-dev.sh`**: Continue.dev configuration wrapper
  - Sets up virtual environment
  - Calls `./ai-gateway continue-dev` (Python module: `ContinueDevService`)

- **`venv.sh`**: Virtual environment management
  - Creates/updates Python venv
  - Installs dependencies from `requirements.txt`

### Shared Modules

- **`src/script_init_bash.sh`**: Common bash initialization
  - Color definitions
  - `check_docker()`: Docker daemon detection and startup (rootless support)
  - `run_standard_checks()`: Unified dependency checks
  - Used by `start.sh`, `stop.sh`, and other scripts

- **`src/check_dependencies.py`**: Python dependency checker
  - Unified checks for all scripts
  - Used by bash scripts via `python3 src/check_dependencies.py`
  - Bash fallback if Python unavailable

### Optional Automation Tools

- **`user.sh`**: System user setup automation
  - Creates system user with proper shell (for rootless Docker)
  - Configures subuid/subgid mappings
  - Sets up rootless Docker
  - **Note**: Experienced admins can do this manually

- **`update.sh`**: File update automation
  - Copies files to installation directory
  - Manages backups
  - Sets permissions
  - **Note**: Experienced admins can manage files manually

## Architecture Principles

### 1. Layer Separation

- **Core**: Domain entities, exceptions, configuration
- **Infrastructure**: External dependencies (files, Docker, logging)
- **Application**: Business logic and use cases

### 2. Dependency Inversion

Infrastructure layer depends on core, not vice versa. Application uses abstractions from infrastructure.

### 3. Repository Pattern

File operations are encapsulated in `FileRepository`, which simplifies testing and changing implementation.

### 4. Centralized Configuration

All configuration is managed through `AppConfig` from `core.config`.

## Usage

### Logging

```python
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)
logger.info("Message")
logger.error("Error")
```

### File Operations

```python
from pathlib import Path
from src.infrastructure.file_repository import FileRepository

repo = FileRepository(Path("/project/root"))
content = repo.read_text(Path("config.yaml"))
repo.write_text(Path("output.txt"), "content")
```

### Configuration

```python
from pathlib import Path
from src.core.config import AppConfig, ResourceProfile, BudgetProfile
from src.application.services import ConfigService

service = ConfigService(Path("/project/root"))
service.set_resource_profile(ResourceProfile.MEDIUM_VPS)
service.set_budget_profile(BudgetProfile.PROD)
config = service.get_config()
```

### Error Handling

```python
from src.core.exceptions import FileOperationError, ConfigurationError

try:
    # operation
except FileOperationError as e:
    logger.error(f"File error: {e}")
```

## Migration from Old Code

Old modules (`utils.py`, `config.py`) are kept for backward compatibility but marked as DEPRECATED. New code should use:

- `infrastructure.logger` instead of `utils.print_*`
- `infrastructure.file_repository` instead of direct file operations
- `core.config` instead of scattered configs
- `core.exceptions` instead of generic Exception

## Testing

The architecture allows easy testing:

1. **Unit tests**: Mocks for infrastructure layer
2. **Integration tests**: Real files and Docker
3. **E2E tests**: Full setup cycle

## Script Execution Flow

### Startup Flow (`start.sh`)

1. **Root check**: Blocks execution as root
2. **Venv check**: Ensures virtual environment exists (creates if needed)
3. **Dependency check**:
   - Primary: Python `check_dependencies.py`
   - Fallback: Bash `run_standard_checks()` from `script_init_bash.sh`
4. **Docker check**: `check_docker()` handles rootless Docker initialization/startup
5. **Call Python service**: `./ai-gateway start` → `StartService.start_containers()`
6. **Check models**: `StartService.check_models_and_suggest_continue_dev()` (if models available via Virtual Key)

### Setup Flow (`setup.sh`)

1. **Venv setup**: Calls `venv.sh` (no code duplication)
2. **Activate venv**: Sources activation script
3. **Run setup**: Calls `./ai-gateway setup` → `SetupService.run_setup()`
4. **Optional Continue.dev**: Offers to run `./continue-dev.sh` → `ContinueDevService.run_setup_interactive()`

### Continue.dev Setup Flow (`continue-dev.sh`)

1. **Venv setup**: Calls `venv.sh` (no code duplication)
2. **Activate venv**: Sources activation script
3. **Run Continue.dev setup**: Calls `./ai-gateway continue-dev` → `ContinueDevService.run_setup_interactive()`
   - Fetches models from LiteLLM API via Virtual Key
   - Generates Continue.dev configuration YAML
   - Generates system prompt markdown

## Design Principles

### Simplicity First

- **No automatic root operations**: Scripts block root execution
- **No automatic file copying**: Work from current directory
- **No automatic user creation**: Admins manage users manually
- **Optional automation**: `user.sh` and `update.sh` are convenience tools

### Dependency Checking

- **Dual approach**: Python (primary) + Bash (fallback)
- **Unified interface**: `check_dependencies.py` for all scripts
- **Shared bash module**: `script_init_bash.sh` for common functions

### Error Handling Strategy

- **Bash**: `set -eo pipefail` for strict error handling
- **Python**: Custom exceptions from `core.exceptions`
- **Clear messages**: User-friendly error messages with actionable steps

## Extension

To add new functionality:

1. **Domain logic** → `core/`
2. **External dependencies** → `infrastructure/`
3. **Business logic** → `application/` (create new service class)
4. **CLI command** → Add to `src/cli.py` (e.g., `run_continue_dev()`)
5. **Bash wrapper** → Create wrapper script that:
   - Sets up venv (uses `venv.sh`)
   - Activates venv
   - Calls `./ai-gateway <command>` (Python module)
6. **Use existing abstractions**: Repository, Logger, ConfigService

### Example: Adding New Service

1. Create service in `src/application/my_service.py`:
   ```python
   class MyService:
       def __init__(self, project_root: Path):
           self.project_root = project_root
       
       def run(self) -> int:
           # Business logic here
           return 0
   ```

2. Add CLI command in `src/cli.py`:
   ```python
   def run_my_service() -> int:
       from src.application.my_service import MyService
       service = MyService(PROJECT_ROOT)
       return service.run()
   ```

3. Create bash wrapper `my_service.sh`:
   ```bash
   #!/bin/bash
   # Setup venv (use venv.sh)
   # Activate venv
   # Call: ./ai-gateway my-service
   ```
