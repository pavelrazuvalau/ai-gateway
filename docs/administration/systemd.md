# Managing AI Gateway with systemd

## Installation

### When is systemd Service Installed?

The systemd service is **optionally installed during setup**:

1. **During `./setup.sh` or `./setup.bat`:**
   - Setup script asks: "Install as systemd service? (Linux only, optional)"
   - If you answer "yes", service is installed automatically
   - Service file is copied to `~/.config/systemd/user/ai-gateway.service`

2. **During `./setup_user.sh` (system user installation):**
   - Service is automatically installed
   - Detects rootless Docker vs regular Docker
   - Uses appropriate service type (user service or system service)

### Manual Installation

If you skipped installation during setup, you can install manually:

**For User Service (rootless Docker or regular user):**

```bash
# 1. Create systemd user directory
mkdir -p ~/.config/systemd/user

# 2. Copy service file
cp ai-gateway.service ~/.config/systemd/user/

# 3. Edit service file to set correct WorkingDirectory
# Replace /path/to/ai-gateway with your actual project path
nano ~/.config/systemd/user/ai-gateway.service

# 4. Enable lingering (allows service to run without login)
loginctl enable-linger $USER

# 5. Reload systemd
systemctl --user daemon-reload

# 6. Enable and start service
systemctl --user enable ai-gateway.service
systemctl --user start ai-gateway.service
```

**For System Service (requires sudo, traditional Docker):**

```bash
# 1. Copy service file
sudo cp ai-gateway.service /etc/systemd/system/

# 2. Edit service file to set correct WorkingDirectory
sudo nano /etc/systemd/system/ai-gateway.service

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable and start service
sudo systemctl enable ai-gateway.service
sudo systemctl start ai-gateway.service
```

### Verify Installation

**Check if service is installed:**
```bash
# User service
systemctl --user list-unit-files | grep ai-gateway

# System service
systemctl list-unit-files | grep ai-gateway
```

**Check service status:**
```bash
# User service
systemctl --user status ai-gateway.service

# System service
sudo systemctl status ai-gateway.service
```

## Setup

AI Gateway is configured as a **systemd user service** (or system service), which means:
- ✅ Automatic startup on system boot
- ✅ Runs even after SSH logout (with lingering enabled)
- ✅ Automatic restart on failures
- ✅ Centralized logging via journald
- ✅ Secure rootless Docker (if using user service)

## Basic Commands

### Service Management

```bash
# Start service
systemctl --user start ai-gateway.service

# Stop service
systemctl --user stop ai-gateway.service

# Restart service
systemctl --user restart ai-gateway.service

# Check status
systemctl --user status ai-gateway.service

# Enable autostart (already enabled)
systemctl --user enable ai-gateway.service

# Disable autostart
systemctl --user disable ai-gateway.service
```

### Viewing Logs

```bash
# Follow logs in real-time
journalctl --user -u ai-gateway.service -f

# View last 50 lines
journalctl --user -u ai-gateway.service -n 50

# View logs since today
journalctl --user -u ai-gateway.service --since today

# View logs with timestamps
journalctl --user -u ai-gateway.service --since "2025-01-01 00:00:00"
```

### Service Status

```bash
# Check if service is running
systemctl --user is-active ai-gateway.service

# Check if service is enabled
systemctl --user is-enabled ai-gateway.service

# Check service status with details
systemctl --user status ai-gateway.service
```

## Service File Location

The service file is located at:
- `~/.config/systemd/user/ai-gateway.service` (user service)

Or if installed system-wide:
- `/etc/systemd/user/ai-gateway.service`

## Service Configuration

The service file (`ai-gateway.service`) is automatically installed during setup. It includes:

- **WorkingDirectory**: Set to project directory (`/opt/ai-gateway` or current directory)
- **ExecStart**: Calls `./start.sh` script
- **Restart**: Automatically restarts on failure
- **RestartSec**: 10 seconds delay before restart
- **Environment**: Sets necessary environment variables for rootless Docker

## Troubleshooting

### Service won't start

1. **Check service status:**
   ```bash
   systemctl --user status ai-gateway.service
   ```

2. **Check logs:**
   ```bash
   journalctl --user -u ai-gateway.service -n 100
   ```

3. **Common issues:**
   - Docker daemon not running: `systemctl --user start docker`
   - Missing `.env` file: Run `./setup.sh` first
   - Permission issues: Check file permissions in project directory

### Service stops after SSH logout

Make sure lingering is enabled for your user:
```bash
loginctl enable-linger $USER
```

This allows user services to run even when not logged in.

### Viewing container logs

The service starts Docker containers. To view container logs:
```bash
# View all container logs
docker compose logs -f

# View specific service logs
docker compose logs -f litellm
docker compose logs -f open-webui
```

## Manual Service Management

If you need to manually manage the service file:

1. **Edit service file:**
   ```bash
   systemctl --user edit ai-gateway.service
   ```

2. **Reload systemd after changes:**
   ```bash
   systemctl --user daemon-reload
   systemctl --user restart ai-gateway.service
   ```

## Benefits of systemd Service

- **Automatic startup**: Service starts automatically on system boot
- **Background operation**: Runs in background, doesn't require active session
- **Automatic recovery**: Restarts automatically on failures
- **Centralized logging**: All logs in one place via journald
- **Resource management**: systemd can manage resource limits
- **Dependency management**: Can depend on other services (e.g., Docker)

## Alternative: Manual Management

If you prefer not to use systemd, you can manage containers manually:

```bash
# Start containers
./start.sh

# Stop containers
./stop.sh

# Check status
docker compose ps
```

However, systemd service is recommended for production deployments as it provides automatic startup and recovery.

