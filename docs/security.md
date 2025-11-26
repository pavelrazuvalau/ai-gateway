# Security Guide

## Basic Security Recommendations

1. **Change default passwords**:
   - Update passwords in `.env` (POSTGRES_PASSWORD, UI_PASSWORD)
   - The master key (LITELLM_MASTER_KEY) is auto-generated, but you can change it

2. **Use Virtual Key instead of Master Key** (REQUIRED):
   - Virtual Key is required for Open WebUI and is more secure than Master Key
   - Master Key has full administrative access - never expose it to applications
   - Virtual Key can be restricted to specific models or teams
   - See [Virtual Key Security](#virtual-key-security) section below
   - See [Virtual Key Guide](configuration/virtual-key.md) for detailed setup

3. **Use Nginx Reverse Proxy** (enabled by default):
   - Nginx is enabled by default during setup for enhanced security
   - Exposes only one external port
   - Open WebUI and LiteLLM API accessible through single port
   - PostgreSQL and internal services remain closed to external access

4. **Keep software updated**:
   - Update Docker images: `docker compose pull`
   - Update Python dependencies: `pip install -U -r requirements.txt`

5. **SSL/HTTPS Configuration** (for production):
   - AI Gateway includes an internal nginx container (HTTP only)
   - For HTTPS/SSL support, use an external nginx server on the host
   - Example configuration available in [`nginx/external-nginx-example.conf`](nginx/external-nginx-example.conf)
   - See [`nginx/README.md`](nginx/README.md) for detailed setup instructions
   - Supports Let's Encrypt (Certbot) for automatic SSL certificate management

**Note:** This is a prototype version. For production use, additional security measures should be implemented (firewall, TLS/HTTPS, etc.).

## Virtual Key Security

### Why Virtual Key is More Secure

**Virtual Key is REQUIRED for Open WebUI** and provides better security than using Master Key directly:

1. **Limited Permissions**:
   - Master Key has full administrative access to LiteLLM
   - Virtual Key can be restricted to specific models, teams, or endpoints
   - If Virtual Key is compromised, damage is limited

2. **Isolation**:
   - Each application can have its own Virtual Key
   - Revoking one key doesn't affect others
   - Master Key remains secure even if Virtual Key is exposed

3. **Auditability**:
   - Usage can be tracked per Virtual Key
   - Easier to identify which application is making requests
   - Better for compliance and monitoring

4. **Revocability**:
   - Virtual Keys can be revoked without affecting Master Key
   - Can rotate keys without system downtime
   - Master Key remains available for administrative tasks

### Security Best Practices

1. **Always use Virtual Key for applications**:
   - ✅ Use Virtual Key for Open WebUI
   - ✅ Use Virtual Key for Continue.dev
   - ✅ Use Virtual Key for other integrations
   - ❌ Never use Master Key in application configurations

2. **Restrict Virtual Key access**:
   - Limit Virtual Key to only the models it needs
   - Use different Virtual Keys for different applications
   - Regularly review and update permissions

3. **Protect Virtual Key**:
   - Store in `.env` file with restricted permissions (600)
   - Never commit to version control
   - Rotate keys periodically
   - Monitor for unusual usage

4. **Master Key protection**:
   - Keep Master Key secret and secure
   - Only use for administrative tasks
   - Never expose in application code or configurations
   - Consider using environment variables or secret management

### When to Use Each Key

**Use Master Key for:**
- LiteLLM Admin UI login
- Administrative operations (creating teams, keys, etc.)
- Direct API testing and debugging
- System configuration

**Use Virtual Key for:**
- Open WebUI integration (REQUIRED)
- Continue.dev integration
- Other application integrations
- Production deployments
- Any scenario where full admin access is not needed

### Key Rotation

Regularly rotating Virtual Keys is a good security practice:

1. **Create new Virtual Key**:
   - In LiteLLM Admin UI, create a new Virtual Key
   - Or run `./virtual-key.sh` to create a new one

2. **Update configuration**:
   - Update `.env` file with new Virtual Key
   - Update application configurations if needed

3. **Restart services**:
   - Restart containers: `./stop.sh && ./start.sh`

4. **Revoke old key**:
   - In LiteLLM Admin UI, revoke the old Virtual Key
   - This prevents any lingering connections from using old key

For detailed Virtual Key setup and configuration, see [Virtual Key Guide](configuration/virtual-key.md).

