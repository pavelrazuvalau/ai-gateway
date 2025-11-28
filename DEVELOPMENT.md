# Development Setup

Инструкции для разработчиков по настройке окружения и использованию инструментов качества кода.

## Установка инструментов разработки

### 1. Установка зависимостей

```bash
# Установить dev зависимости
pip install -r requirements-dev.txt

# Или через pyproject.toml
pip install -e ".[dev]"
```

### 2. Настройка pre-commit hooks

```bash
# Установить hooks
pre-commit install

# Запустить на всех файлах (первый раз)
pre-commit run --all-files
```

## Использование инструментов

### Ruff (линтер и форматтер)

```bash
# Проверить код
ruff check .

# Автоматически исправить проблемы
ruff check --fix .

# Форматировать код
ruff format .

# Проверить конкретный файл
ruff check src/cli.py
```

### Black (форматтер)

```bash
# Проверить форматирование
black --check .

# Отформатировать код
black .

# Проверить конкретный файл
black --check src/cli.py
```

### MyPy (проверка типов)

```bash
# Проверить типы во всем проекте
mypy src/

# Проверить конкретный модуль
mypy src/core/

# Показать все ошибки
mypy src/ --show-error-codes
```

### Pytest (тестирование)

```bash
# Запустить все тесты
pytest

# С покрытием
pytest --cov=src --cov-report=term-missing

# Конкретный тест
pytest tests/unit/test_core.py

# Только unit тесты
pytest -m unit

# Только integration тесты
pytest -m integration
```

## Non-interactive режим для E2E тестов

Non-interactive режим позволяет запускать скрипты и команды без интерактивных промптов, что критично для автоматизированного тестирования и CI/CD.

### Переменные окружения

Основная переменная окружения:

- `NON_INTERACTIVE=1` - включает non-interactive режим для всех поддерживающих его скриптов и команд

### Shell скрипты

Следующие shell скрипты поддерживают `NON_INTERACTIVE=1`:

#### `setup.sh`

```bash
# Запуск setup без интерактивных вопросов
NON_INTERACTIVE=1 ./setup.sh
```

В non-interactive режиме:

- Использует существующий `.env` файл, если он есть
- Использует значения по умолчанию для всех настроек:
  - Resource Profile: `MEDIUM_VPS`
  - Budget Profile: `test`
  - Ports: значения по умолчанию
  - Nginx: включен по умолчанию
  - Systemd: не устанавливается

#### `start.sh`

```bash
# Запуск без подтверждений
NON_INTERACTIVE=1 ./start.sh
```

В non-interactive режиме:

- Автоматически отвечает "yes" на все подтверждения
- Использует `AUTO_YES="y"` для автоматических ответов

#### `stop.sh`

```bash
# Остановка без подтверждений
NON_INTERACTIVE=1 ./stop.sh
```

В non-interactive режиме:

- Автоматически отвечает "yes" на все подтверждения

#### `virtual-key.sh` и `continue-dev.sh`

Эти скрипты передают `NON_INTERACTIVE` в Python модули через переменную окружения:

```bash
# Virtual Key setup
NON_INTERACTIVE=1 ./virtual-key.sh

# Continue.dev setup
NON_INTERACTIVE=1 ./continue-dev.sh
```

### Python CLI команды

CLI команды поддерживают как переменную окружения, так и флаг `--non-interactive`:

#### Setup команда

```bash
# Через переменную окружения
NON_INTERACTIVE=1 ./ai-gateway setup

# Через флаг
./ai-gateway setup --non-interactive
```

#### Continue.dev команда

```bash
# Через переменную окружения
NON_INTERACTIVE=1 ./ai-gateway continue-dev

# Через флаг
./ai-gateway continue-dev --non-interactive
```

### Python модули

Python модули поддерживают параметр `non_interactive`:

#### `SetupService.run_setup()`

```python
from src.application.setup_service import SetupService

service = SetupService(project_root)
service.run_setup(non_interactive=True)
```

#### `InteractiveSetup` методы

```python
from src.application.setup_service import InteractiveSetup

setup = InteractiveSetup(project_root)

# Все методы поддерживают non_interactive параметр
reuse_env, force_recreate, existing_env = setup.ask_env_mode(non_interactive=True)
budget_profile = setup.ask_budget_profile(reuse_env, existing_env, non_interactive=True)
tavily_api_key = setup.ask_tavily_api_key(existing_env, non_interactive=True)
install_systemd = setup.ask_systemd_installation(non_interactive=True)
```

#### `ContinueDevService.run_setup_interactive()`

```python
from src.application.continue_dev_service import ContinueDevService

service = ContinueDevService(project_root)
service.run_setup_interactive(non_interactive=True)
```

#### Другие модули

```python
from src.config import select_resource_profile
from src.ports import configure_ports
from src.virtual_key import setup_virtual_key_interactive
from src.infrastructure.output import ask_yes_no

# Все поддерживают non_interactive параметр
profile = select_resource_profile(non_interactive=True)
port_config = configure_ports(non_interactive=True)
virtual_key = setup_virtual_key_interactive(non_interactive=True)
result = ask_yes_no("Continue?", default=True, non_interactive=True)
```

### Значения по умолчанию в non-interactive режиме

Когда `non_interactive=True` или `NON_INTERACTIVE=1`, используются следующие значения по умолчанию:

| Настройка | Значение по умолчанию |
|-----------|----------------------|
| Resource Profile | `MEDIUM_VPS` |
| Budget Profile | `test` |
| Nginx | Включен |
| Ports | Значения по умолчанию из конфигурации |
| Systemd | Не устанавливается |
| Tavily API Key | Пропускается (опционально) |
| Virtual Key | Пытается создать автоматически |

### Использование в тестах

Пример использования в E2E тестах:

```python
import os
import pytest
from pathlib import Path

def test_setup_non_interactive(tmp_path):
    """Test setup in non-interactive mode."""
    # Установить переменную окружения
    os.environ["NON_INTERACTIVE"] = "1"

    try:
        from src.application.setup_service import SetupService

        service = SetupService(tmp_path)
        service.run_setup(non_interactive=True)

        # Проверить, что .env создан
        assert (tmp_path / ".env").exists()
    finally:
        # Очистить переменную окружения
        if "NON_INTERACTIVE" in os.environ:
            del os.environ["NON_INTERACTIVE"]
```

### Проверка non-interactive режима

Для проверки, работает ли код в non-interactive режиме:

```python
from src.infrastructure.output import is_non_interactive

if is_non_interactive():
    # Non-interactive режим активен
    pass
```

Функция `is_non_interactive()` проверяет переменную окружения `NON_INTERACTIVE` и возвращает `True`, если она установлена в `"1"`.

## Pre-commit hooks

Hooks автоматически запускаются при каждом коммите. Они проверяют:

- Форматирование кода (Ruff, Black)
- Линтинг (Ruff)
- Типы (MyPy)
- Общие проверки файлов (trailing whitespace, EOF, YAML, JSON, TOML)
- Markdown linting

### Ручной запуск hooks

```bash
# На всех файлах
pre-commit run --all-files

# На staged файлах (как при коммите)
pre-commit run

# Конкретный hook
pre-commit run ruff --all-files
```

## CI/CD Integration

Инструменты можно интегрировать в CI/CD pipeline:

```yaml
# Пример для GitHub Actions
- name: Run Ruff
  run: ruff check .

- name: Run Black check
  run: black --check .

- name: Run MyPy
  run: mypy src/

- name: Run tests
  run: pytest --cov=src --cov-report=xml
```

## Конфигурация

Все настройки находятся в `pyproject.toml`:

- `[tool.ruff]` - настройки Ruff
- `[tool.black]` - настройки Black
- `[tool.mypy]` - настройки MyPy
- `[tool.pytest.ini_options]` - настройки Pytest
- `[tool.coverage.*]` - настройки покрытия

## Troubleshooting

### MyPy не находит импорты

Добавьте в `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["module_name.*"]
ignore_missing_imports = true
```

### Pre-commit не работает

```bash
# Переустановить hooks
pre-commit uninstall
pre-commit install

# Обновить hooks
pre-commit autoupdate
```

### Ruff находит слишком много ошибок

Можно временно игнорировать правила:

```toml
[tool.ruff]
ignore = ["E501", "F401"]  # Игнорировать конкретные правила
```

Или в коде:

```python
# ruff: noqa: E501  # Игнорировать для этой строки
```
