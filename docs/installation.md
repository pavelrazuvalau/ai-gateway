# AI Gateway Installation with System User

This guide describes the installation of AI Gateway using a system user `aigateway` with proper permission configuration.

## Requirements

- Linux system (Ubuntu/Debian/Fedora/Arch, etc.)
- Docker and Docker Compose installed
- Root privileges (sudo)

### ⚠️ Proxmox LXC Containers

**Rootless Docker is not reliably supported in unprivileged Proxmox LXC containers** due to kernel-level restrictions on user namespaces (`uid_map` access). Even with proper `subuid`/`subgid` configuration and AppArmor settings, the kernel may still deny access to user namespaces.

**Recommendations:**
- **Use a full VM** instead of an LXC container for running AI Gateway
- **Or use a privileged LXC container** (less secure, but may work with rootless Docker)

If you encounter "Permission denied" errors when initializing rootless Docker in an unprivileged LXC container, this is expected behavior. The recommended solution is to deploy AI Gateway in a VM or use a privileged container.

## Step 1: User Setup and Permissions Configuration

Run the setup script with root privileges:

```bash
sudo ./setup_user.sh
```

Or simply run it (it will prompt for sudo if needed):

```bash
./setup_user.sh
```

The script will:
1. Create system user `aigateway` with `/usr/sbin/nologin` shell
2. Add user to `docker` group
3. Copy project files to `/opt/ai-gateway`
4. Set proper ownership and permissions
5. Install and configure systemd service

## Step 2: Initial Configuration

Run the interactive setup as user `aigateway`:

```bash
sudo -u aigateway /opt/ai-gateway/setup.sh
```

This will guide you through:
- Resource profile selection (Desktop/Small VPS/Medium VPS/Large VPS)
- Budget configuration (Test/Prod/Unlimited)
- Port configuration (with optional random high ports for security)
- Nginx reverse proxy setup (optional)
- SSL/HTTPS configuration (optional)

**Note:** All configuration is interactive. The setup will create `.env` and `config.yaml` files in `/opt/ai-gateway`.

**SSL/HTTPS Setup:** For production deployments with SSL/HTTPS support, see the external nginx configuration example in [`docs/nginx/external-nginx-example.conf`](../docs/nginx/external-nginx-example.conf) and detailed setup instructions in [`docs/nginx/README.md`](../docs/nginx/README.md).

## Step 3: Starting the Service

### Manual Start

```bash
sudo -u aigateway /opt/ai-gateway/start.sh
```

### Automatic Start via systemd

The `setup_user.sh` script automatically installs the systemd service. It detects rootless Docker and uses the appropriate service type:

- **Rootless Docker**: Uses systemd **user service** (runs as user, no root)
- **Regular Docker**: Uses systemd **system service** (traditional)

#### For Rootless Docker (User Service)

The service is installed at: `~/.config/systemd/user/ai-gateway.service`

**Manual installation** (if needed):

```bash
# Copy service file to user directory
sudo -u aigateway mkdir -p /opt/ai-gateway/.config/systemd/user
sudo cp /opt/ai-gateway/ai-gateway.service /opt/ai-gateway/.config/systemd/user/
sudo chown aigateway:aigateway /opt/ai-gateway/.config/systemd/user/ai-gateway.service

# Enable lingering (allows user services without login)
sudo loginctl enable-linger aigateway

# Reload user systemd
sudo -u aigateway systemctl --user daemon-reload

# Enable and start
sudo -u aigateway systemctl --user enable ai-gateway
sudo -u aigateway systemctl --user start ai-gateway
```

**Service Management**:

```bash
# Start
sudo -u aigateway systemctl --user start ai-gateway

# Stop
sudo -u aigateway systemctl --user stop ai-gateway

# Restart
sudo -u aigateway systemctl --user restart ai-gateway

# View logs
sudo -u aigateway journalctl --user -u ai-gateway -f

# Check status
sudo -u aigateway systemctl --user status ai-gateway
```

#### For Regular Docker (System Service)

The service is installed at: `/etc/systemd/system/ai-gateway.service`

**Manual installation** (if needed):

```bash
# Copy service file
sudo cp /opt/ai-gateway/ai-gateway.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable ai-gateway.service
sudo systemctl start ai-gateway.service
```

**Service Management**:

```bash
# Start
sudo systemctl start ai-gateway

# Stop
sudo systemctl stop ai-gateway

# Restart
sudo systemctl restart ai-gateway

# View logs
sudo journalctl -u ai-gateway -f

# Check status
sudo systemctl status ai-gateway
```

## Permission Structure

After installation:

- **Owner**: `aigateway:aigateway`
- **Directories**: `755` (rwxr-xr-x)
- **Scripts**: `755` (executable)
- **Config files**: `644` (readable)
- **`.env`**: `600` (owner only - contains sensitive data)
- **`config.yaml`**: `644` (readable by owner and group - as per CHANGELOG)

## Docker Access

The setup script automatically detects and prefers **rootless Docker** for enhanced security. If rootless Docker is available, it will be configured. Otherwise, it falls back to regular Docker with group access.

### Rootless Docker (Preferred)

If rootless Docker is detected:

1. Rootless Docker daemon runs as user `aigateway` (no root privileges)
2. Docker socket is located at: `~/.docker/run/docker.sock`
3. Systemd user service is used instead of system service
4. Enhanced security - no root access required

**Initialize rootless Docker** (if not already done):

```bash
sudo -u aigateway dockerd-rootless-setuptool.sh install
```

**Start rootless Docker daemon**:

```bash
sudo -u aigateway systemctl --user start docker
sudo -u aigateway systemctl --user enable docker  # Enable on boot
```

**Verify access**:

```bash
sudo -u aigateway docker ps
```

### Regular Docker (Fallback)

If rootless Docker is not available, the user is added to the `docker` group:

1. Restart Docker:

```bash
sudo systemctl restart docker
```

2. Or log out and log back in to refresh group membership

3. Verify access:

```bash
sudo -u aigateway docker ps
```

## Application Updates

To update application files (preserves your configuration):

```bash
# 1. Update source files in your working directory
cd /path/to/ai-gateway
git pull  # or other update method

# 2. Run setup_user.sh again (preserves .env and config.yaml)
sudo ./setup_user.sh

# 3. Restart the application
sudo -u aigateway /opt/ai-gateway/start.sh

# Or restart the systemd service
sudo -u aigateway systemctl --user restart ai-gateway
```

**Important:** The `setup_user.sh` script automatically preserves your `.env` and `config.yaml` files when updating, so your configuration will not be lost.

## Security

- User `aigateway` cannot log in (nologin shell)
- Sensitive files have appropriate permissions:
- `.env`: `600` (owner only - contains API keys and passwords)
- `config.yaml`: `644` (readable by owner and group - contains configuration, no sensitive data)
- Service runs as unprivileged user
- **Rootless Docker preferred** - Docker daemon runs without root privileges
- Docker access through rootless mode or group (no sudo required)

## Troubleshooting

### User Cannot Access Docker

**For rootless Docker**:

```bash
# Check if rootless Docker is running
sudo -u aigateway systemctl --user status docker

# Start rootless Docker
sudo -u aigateway systemctl --user start docker

# Initialize if not done
sudo -u aigateway dockerd-rootless-setuptool.sh install
```

**For regular Docker**:

```bash
# Check groups
groups aigateway

# Ensure user is in docker group
sudo usermod -aG docker aigateway
sudo systemctl restart docker
```

### Permission Issues

```bash
# Fix permissions
sudo chown -R aigateway:aigateway /opt/ai-gateway
sudo find /opt/ai-gateway -type d -exec chmod 755 {} \;
sudo find /opt/ai-gateway -type f -name "*.sh" -exec chmod 755 {} \;
```

### Viewing Logs

**For rootless Docker (user service)**:

```bash
# Systemd user service logs
sudo -u aigateway journalctl --user -u ai-gateway -f

# Docker container logs
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs -f
```

**For regular Docker (system service)**:

```bash
# Systemd system service logs
sudo journalctl -u ai-gateway -f

# Docker container logs
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs -f
```

### Diagnosing Container Errors

If you see container errors (e.g., `✘ Container litellm-proxy Error`), use these commands to diagnose:

**1. Check container status:**

```bash
# For rootless Docker
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml ps

# For regular Docker (if running as aigateway user)
cd /opt/ai-gateway && docker compose ps
```

**2. View logs for specific container:**

```bash
# View logs for litellm-proxy container
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs litellm-proxy

# View last 100 lines with timestamps
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs --tail=100 -t litellm-proxy

# Follow logs in real-time
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs -f litellm-proxy
```

**3. View logs for all containers:**

```bash
# All containers
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs

# Last 50 lines from all containers
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs --tail=50

# Follow all logs
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs -f
```

**4. Check specific container errors:**

```bash
# Inspect container (shows detailed info including error messages)
sudo -u aigateway docker inspect litellm-proxy

# Check container exit code
sudo -u aigateway docker inspect litellm-proxy --format='{{.State.ExitCode}}'

# View container events
sudo -u aigateway docker events --filter container=litellm-proxy
```

**5. Common issues and solutions:**

**Container exits immediately:**
```bash
# Check why container exited
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml logs litellm-proxy | tail -50

# Restart container
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml restart litellm-proxy
```

**Configuration errors:**
```bash
# Check .env file
sudo -u aigateway cat /opt/ai-gateway/.env | grep -i litellm

# Check config.yaml
sudo -u aigateway cat /opt/ai-gateway/config.yaml
```

**Port conflicts:**
```bash
# Check if port is already in use
sudo netstat -tulpn | grep :4000
# or
sudo ss -tulpn | grep :4000
```

**6. Quick diagnostic script:**

```bash
# Run this to get comprehensive diagnostic info
cd /opt/ai-gateway
echo "=== Container Status ==="
sudo -u aigateway docker compose ps
echo ""
echo "=== Recent Errors ==="
sudo -u aigateway docker compose logs --tail=20 | grep -i error
echo ""
echo "=== litellm-proxy Logs (last 30 lines) ==="
sudo -u aigateway docker compose logs --tail=30 litellm-proxy
```

## Uninstallation

For complete removal:

```bash
# 1. Stop and remove containers
sudo -u aigateway /opt/ai-gateway/stop.sh
sudo -u aigateway docker compose -f /opt/ai-gateway/docker-compose.yml down -v

# 2. Stop and remove systemd service
# For rootless Docker (user service):
sudo -u aigateway systemctl --user stop ai-gateway
sudo -u aigateway systemctl --user disable ai-gateway
sudo rm /opt/ai-gateway/.config/systemd/user/ai-gateway.service 2>/dev/null || true

# For regular Docker (system service):
sudo systemctl stop ai-gateway
sudo systemctl disable ai-gateway
sudo rm /etc/systemd/system/ai-gateway.service
sudo systemctl daemon-reload

# 3. Remove user and directory
sudo userdel -r aigateway
sudo rm -rf /opt/ai-gateway
```
