# E2E Tests - Локальный запуск

## Концепция

**E2E тесты запускаются ЛОКАЛЬНО** на машине разработчика для проверки полного цикла работы системы.

**Prod сервер используется только для:**
- Сбора информации (мониторинг, логи, метрики)
- Проверки реального поведения системы
- **НЕ для запуска тестов**

## Требования

- Docker и Docker Compose установлены и запущены
- Python 3.8+
- Достаточно места на диске (~2-3 GB для временных контейнеров)
- Достаточно RAM (минимум 2.5GB свободно для Small VPS профиля)

**Примечание**: E2E тесты используют **Small VPS** профиль по умолчанию (1 worker, ~2.0-2.5GB RAM) для быстрого выполнения и минимального потребления ресурсов.

## Быстрый старт

```bash
# 1. Активировать виртуальное окружение
source venv/bin/activate

# 2. Установить зависимости (если еще не установлены)
pip install -r requirements-dev.txt

# 3. Запустить все E2E тесты
pytest tests/e2e/ -v -m e2e

# Или запустить конкретный тест
pytest tests/e2e/test_full_cycle.py -v
pytest tests/e2e/test_api_with_mocks.py -v
```

## Что тестируется

1. ✅ Setup в non-interactive режиме
2. ✅ Запуск контейнеров
3. ✅ Health checks всех сервисов (PostgreSQL, LiteLLM, Open WebUI, Nginx)
4. ✅ HTTP endpoints доступность
5. ✅ API endpoints (базовые тесты)
6. ✅ Остановка контейнеров
7. ✅ Изоляция контейнеров (через COMPOSE_PROJECT_NAME)
8. ✅ Очистка ресурсов после тестов

## Изоляция тестов

Каждый тест запускается в изолированной временной директории с уникальным `COMPOSE_PROJECT_NAME`, что гарантирует:
- Отсутствие конфликтов между тестами
- Отсутствие конфликтов с существующими контейнерами
- Автоматическую очистку после завершения

## Мониторинг выполнения

В отдельном терминале можно мониторить выполнение:

```bash
# Смотреть контейнеры в реальном времени
watch -n 2 'docker ps | grep ai-gateway-e2e'

# Или использовать скрипт мониторинга
./monitor_e2e_tests.sh
```

## Ожидаемое время выполнения

- Один тест: ~2-5 минут (setup + start + health checks + stop)
- Все тесты: ~10-15 минут (зависит от количества тестов)

**Примечание**: Использование Small VPS (1 worker) ускоряет запуск контейнеров и уменьшает потребление ресурсов.

## Resource Profile

E2E тесты используют **Small VPS** профиль по умолчанию:
- **Workers**: 1 (минимальное потребление ресурсов)
- **RAM**: ~2.0-2.5GB (включая системные накладные расходы)
- **CPU**: 2 cores

Для переопределения профиля используйте env var:
```bash
# Использовать Medium VPS (2 workers, ~3.3GB)
E2E_RESOURCE_PROFILE=medium pytest tests/e2e/ -v -m e2e

# Использовать Large VPS (6 workers, ~5.7GB)
E2E_RESOURCE_PROFILE=large pytest tests/e2e/ -v -m e2e
```

## Проверка результатов

После выполнения проверьте:

```bash
# 1. Все тесты прошли
pytest tests/e2e/ -v -m e2e --tb=short

# 2. Нет остаточных контейнеров
docker ps -a | grep ai-gateway-e2e || echo "✅ OK - no leftover containers"

# 3. Нет остаточных сетей
docker network ls | grep ai-gateway-e2e || echo "✅ OK - no leftover networks"
```

## Очистка (если что-то пошло не так)

```bash
# Остановить все E2E контейнеры
docker ps -a --filter "name=ai-gateway-e2e" --format "{{.ID}}" | xargs -r docker rm -f

# Удалить все E2E сети
docker network ls --filter "name=ai-gateway-e2e" --format "{{.ID}}" | xargs -r docker network rm
```

## Документация

- [DEVELOPMENT.md](../../DEVELOPMENT.md) - общая информация о разработке
- [IMPROVEMENT_PLAN.md](../../IMPROVEMENT_PLAN.md#Этап-6) - детали реализации E2E тестов
- [E2E_TESTS_CHECK.md](../../E2E_TESTS_CHECK.md) - подробная инструкция по проверке

