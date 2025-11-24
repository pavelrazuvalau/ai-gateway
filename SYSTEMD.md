# Управление AI Gateway через systemd

## Настройка

AI Gateway настроен как **systemd user service**, что означает:
- ✅ Автоматический запуск при старте системы
- ✅ Работает даже после выхода из SSH
- ✅ Автоматический перезапуск при сбоях
- ✅ Централизованное логирование через journald
- ✅ Безопасный rootless Docker

## Основные команды

### Управление сервисом

```bash
# Запустить сервис
systemctl --user start ai-gateway.service

# Остановить сервис
systemctl --user stop ai-gateway.service

# Перезапустить сервис
systemctl --user restart ai-gateway.service

# Проверить статус
systemctl --user status ai-gateway.service

# Включить автозапуск (уже включено)
systemctl --user enable ai-gateway.service

# Отключить автозапуск
systemctl --user disable ai-gateway.service
```

### Просмотр логов

```bash
# Последние 50 строк логов
journalctl --user -u ai-gateway.service -n 50

# Логи в реальном времени
journalctl --user -u ai-gateway.service -f

# Логи за сегодня
journalctl --user -u ai-gateway.service --since today

# Логи за последний час
journalctl --user -u ai-gateway.service --since "1 hour ago"
```

### Docker команды

Сервис автоматически управляет Docker контейнерами, но вы также можете использовать:

```bash
# Посмотреть запущенные контейнеры
docker ps

# Посмотреть логи контейнера
docker logs litellm-proxy -f
docker logs open-webui -f
docker logs litellm-postgres -f
docker logs litellm-nginx -f

# Войти в контейнер
docker exec -it litellm-proxy sh
```

## Файл конфигурации

Файл сервиса: `~/.config/systemd/user/ai-gateway.service`

```ini
[Unit]
Description=AI Gateway - LiteLLM, Open WebUI, PostgreSQL, Nginx
Documentation=https://github.com/pavelrazuvalau/ai-gateway
After=docker.service
Wants=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/ai-gateway

# Start command (docker compose up -d)
ExecStart=/usr/bin/docker compose -f %h/ai-gateway/docker-compose.yml up -d --remove-orphans

# Stop command (docker compose down)
ExecStop=/usr/bin/docker compose -f %h/ai-gateway/docker-compose.yml down

# Restart policy
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

## Обновление после изменений

После изменений в `.env`, `config.yaml` или `docker-compose.yml`:

```bash
# Просто перезапустите сервис
systemctl --user restart ai-gateway.service

# Или пересоздайте контейнеры
cd ~/ai-gateway
docker compose down
systemctl --user start ai-gateway.service
```

## Обновление из Git

```bash
cd ~/ai-gateway
git pull
systemctl --user restart ai-gateway.service
```

## Переустановка сервиса

Если нужно изменить systemd service файл:

```bash
# 1. Отредактировать файл
nano ~/.config/systemd/user/ai-gateway.service

# 2. Перезагрузить конфигурацию systemd
systemctl --user daemon-reload

# 3. Перезапустить сервис
systemctl --user restart ai-gateway.service
```

## Важно: Lingering

Для работы сервиса после выхода из SSH включен **lingering**:

```bash
# Проверить статус lingering
loginctl show-user $USER | grep Linger

# Должно быть: Linger=yes
```

Если нужно отключить (контейнеры остановятся после выхода):

```bash
loginctl disable-linger $USER
```

## Полное удаление

Если нужно полностью удалить сервис:

```bash
# 1. Остановить и отключить
systemctl --user stop ai-gateway.service
systemctl --user disable ai-gateway.service

# 2. Удалить файл сервиса
rm ~/.config/systemd/user/ai-gateway.service

# 3. Перезагрузить systemd
systemctl --user daemon-reload

# 4. Удалить Docker контейнеры и volumes (опционально)
cd ~/ai-gateway
docker compose down -v
```

## Troubleshooting

### Сервис не запускается

```bash
# Посмотреть детальные логи
journalctl --user -u ai-gateway.service -xe

# Проверить Docker
docker info

# Проверить файлы
ls -la ~/ai-gateway/
```

### Контейнеры не работают после перезагрузки

```bash
# Проверить, что lingering включен
loginctl show-user $USER | grep Linger

# Проверить статус сервиса
systemctl --user status ai-gateway.service

# Проверить user systemd
systemctl --user status
```

### Изменения не применяются

```bash
# Пересоздать контейнеры
systemctl --user stop ai-gateway.service
cd ~/ai-gateway
docker compose down
docker compose pull  # обновить образы
systemctl --user start ai-gateway.service
```

## Старые скрипты start.sh / stop.sh

⚠️ **Больше не нужно использовать** `start.sh` и `stop.sh` напрямую!

Вместо них используйте команды systemd выше. Однако скрипты остаются в репозитории для ручного управления при необходимости.

