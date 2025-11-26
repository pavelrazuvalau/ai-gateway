# Configuration Examples

<!--
Tags for AI agents:
- configuration
- examples
- env-examples
- setup-examples
- production-config
- development-config
-->

Example configurations for different scenarios and use cases.

## Minimal Development Configuration

### `.env` File

```bash
# Required variables
LITELLM_MASTER_KEY=sk-your-master-key-here
POSTGRES_USER=litellm
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_DB=litellm
POSTGRES_PORT=5432

# Virtual Key (created after setup)
VIRTUAL_KEY=sk-your-virtual-key-here

# Ports (with Nginx)
NGINX_HTTP_PORT=3000
LITELLM_EXTERNAL_PORT=4000

# Optional: UI credentials
UI_USERNAME=admin
UI_PASSWORD=your-secure-password-here
WEBUI_SECRET_KEY=your-secret-key-here
```

### Resource Profile: Desktop

```bash
# No resource limits for local development
# Set during setup: ./setup.sh
# Or in .env:
RESOURCE_PROFILE=local
```

## Production Configuration

### `.env` File

```bash
# Security
LITELLM_MASTER_KEY=sk-very-secure-master-key-min-32-chars
VIRTUAL_KEY=sk-very-secure-virtual-key-min-32-chars

# Database
POSTGRES_USER=litellm_prod
POSTGRES_PASSWORD=very-secure-password-min-16-chars
POSTGRES_DB=litellm_prod
POSTGRES_PORT=5432

# Ports (with Nginx)
NGINX_HTTP_PORT=8080
LITELLM_EXTERNAL_PORT=4000

# UI Security
UI_USERNAME=admin_prod
UI_PASSWORD=very-secure-password-min-16-chars
WEBUI_SECRET_KEY=very-secure-secret-key-min-32-chars

# Resource Profile
RESOURCE_PROFILE=medium_vps  # or large_vps for teams

# Budget Profile
BUDGET_PROFILE=prod  # $200/month

# API Keys (add as needed)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

### Resource Profile: Medium VPS

```bash
# Set during setup or in .env
RESOURCE_PROFILE=medium_vps
# Provides: 4GB RAM, 4 CPU cores
```

### Resource Profile: Large VPS

```bash
# Set during setup or in .env
RESOURCE_PROFILE=large_vps
# Provides: 8GB+ RAM, 8 CPU cores
```

## Multi-Provider Configuration

### `.env` File with Multiple Providers

```bash
# Core configuration
LITELLM_MASTER_KEY=sk-...
VIRTUAL_KEY=sk-...
POSTGRES_USER=litellm
POSTGRES_PASSWORD=...
POSTGRES_DB=litellm
POSTGRES_PORT=5432

# Ports
NGINX_HTTP_PORT=3000
LITELLM_EXTERNAL_PORT=4000

# Provider API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
MISTRAL_API_KEY=...
GROQ_API_KEY=...
DEEPSEEK_API_KEY=...
TOGETHER_API_KEY=...
PERPLEXITY_API_KEY=...
```

### Adding Providers via LiteLLM Admin UI

1. Access LiteLLM Admin UI: `http://localhost:4000/ui`
2. Go to "Providers" section
3. Add provider with API key
4. Models will be automatically available

## Budget Control Configuration

### Test Budget ($15/month)

```bash
BUDGET_PROFILE=test
```

### Production Budget ($200/month)

```bash
BUDGET_PROFILE=prod
```

### Unlimited Budget ($1000/month)

```bash
BUDGET_PROFILE=unlimited
```

## Security Configuration

### Strong Passwords and Keys

```bash
# Generate secure keys (minimum lengths)
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)  # 64+ chars
VIRTUAL_KEY=sk-$(openssl rand -hex 32)  # 64+ chars
POSTGRES_PASSWORD=$(openssl rand -base64 24)  # 32+ chars
UI_PASSWORD=$(openssl rand -base64 24)  # 32+ chars
WEBUI_SECRET_KEY=$(openssl rand -hex 32)  # 64+ chars
```

### File Permissions

```bash
# Set secure permissions
chmod 600 .env
chmod 644 config.yaml
chmod 600 docker-compose.override.yml
```

## Network Configuration

### Local Network Access

```bash
# Allow access from local network
# No additional configuration needed
# Access via: http://YOUR_IP:PORT
```

### Firewall Rules (Linux - firewalld)

```bash
# Allow HTTP traffic
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

### Firewall Rules (Linux - ufw)

```bash
# Allow HTTP traffic
sudo ufw allow 3000/tcp
```

## Docker Compose Override Example

### `docker-compose.override.yml`

```yaml
services:
  litellm:
    environment:
      - LITELLM_LOG_LEVEL=INFO  # DEBUG for troubleshooting
      - SET_VERBOSE=False
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
        reservations:
          memory: 1G
          cpus: '1'

  postgres:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1'
        reservations:
          memory: 256M
          cpus: '0.5'

  open-webui:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1'
        reservations:
          memory: 512M
          cpus: '0.5'
```

## Environment-Specific Configurations

### Development

```bash
# .env.development
LITELLM_LOG_LEVEL=DEBUG
SET_VERBOSE=True
RESOURCE_PROFILE=local
BUDGET_PROFILE=test
```

### Staging

```bash
# .env.staging
LITELLM_LOG_LEVEL=INFO
SET_VERBOSE=False
RESOURCE_PROFILE=medium_vps
BUDGET_PROFILE=prod
```

### Production

```bash
# .env.production
LITELLM_LOG_LEVEL=WARNING
SET_VERBOSE=False
RESOURCE_PROFILE=large_vps
BUDGET_PROFILE=unlimited
```

## Configuration Validation

### Check Configuration

```bash
# Verify .env file
grep -E "^[A-Z_]+=" .env

# Check required variables
required_vars=(
  "LITELLM_MASTER_KEY"
  "POSTGRES_USER"
  "POSTGRES_PASSWORD"
  "POSTGRES_DB"
  "POSTGRES_PORT"
)

for var in "${required_vars[@]}"; do
  if ! grep -q "^${var}=" .env; then
    echo "Missing: $var"
  fi
done
```

## Related Documentation

- **[Configuration Guide](../configuration.md)** - Complete configuration reference
- **[System Requirements](../system-requirements.md)** - Resource profiles and requirements
- **[Security Guide](../security.md)** - Security best practices
- **[Troubleshooting](../troubleshooting.md)** - Configuration troubleshooting

