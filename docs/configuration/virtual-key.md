# Virtual Key Guide

## What is Virtual Key?

**Virtual Key** is a restricted API key in LiteLLM that provides secure, limited access to the LiteLLM API. It's the recommended way for Open WebUI and other applications to connect to LiteLLM.

### Key Features

- **Restricted Permissions**: Can be limited to specific models, teams, or endpoints
- **More Secure**: Safer than using Master Key directly in applications
- **Team-Based**: Can be associated with teams for better organization
- **Auditable**: Usage can be tracked per key
- **Revocable**: Can be revoked without affecting Master Key

## Why Virtual Key is Required

**Virtual Key is REQUIRED for Open WebUI to work.** Here's why:

1. **Security**: Open WebUI needs API access, but using Master Key directly is a security risk
2. **Isolation**: Virtual Key allows you to limit what Open WebUI can access
3. **Best Practice**: LiteLLM recommends using Virtual Keys for all application integrations
4. **Compliance**: Some setups require separate keys for different applications

## Virtual Key vs Master Key

| Feature | Master Key | Virtual Key |
|---------|-----------|-------------|
| **Purpose** | Full administrative access | Limited application access |
| **Permissions** | All operations | Can be restricted |
| **Usage** | Admin UI, direct API calls | Application integrations |
| **Security** | High risk if exposed | Lower risk if exposed |
| **Revocation** | Affects all access | Only affects specific key |
| **Scope** | System-wide | Team/model-specific |

### When to Use Each

**Use Master Key for:**
- LiteLLM Admin UI login
- Administrative operations
- Direct API testing
- System configuration

**Use Virtual Key for:**
- Open WebUI integration
- Continue.dev integration
- Other application integrations
- Production deployments

## Creating Virtual Key

### Automatic Creation (Recommended)

The easiest way to create a Virtual Key is using the provided script:

```bash
# Linux/macOS
./virtual-key.sh

# Windows
virtual-key.bat
```

**What the script does:**
1. Checks if containers are running
2. Tries to run Virtual Key creation inside Docker container (avoids port issues)
3. If that fails, connects to LiteLLM API from host
4. Creates a team "Open WebUI Team" (if needed)
5. Creates a Virtual Key "Open WebUI Key" for the team
6. Saves the Virtual Key to `.env` file
7. Updates `FIRST_RUN` flag from `yes` to `no`

**Prerequisites:**
- Containers must be running (`./start.sh`)
- LiteLLM must be accessible (may take 45+ seconds after container start)
- Master Key must be in `.env` file

**How it works:**
- Script first tries to run inside `litellm-proxy` container (uses Docker network directly)
- This avoids port configuration issues
- Falls back to host-based API calls if container method fails
- If both fail, provides manual instructions

### Manual Creation

If automatic creation fails, you can create Virtual Key manually:

1. **Open LiteLLM Admin UI**
   - URL: http://localhost:4000/ui (or your configured port)
   - Login with Master Key from `.env` file

2. **Create Team** (optional but recommended):
   - Go to **Teams/Users** section
   - Click "Create Team" or "Add Team"
   - Enter team name (e.g., "Open WebUI Team")
   - Save

3. **Create Virtual Key**:
   - In Teams section, select your team
   - Click "Create Key" or "Add Virtual Key"
   - Enter key name (e.g., "Open WebUI Key")
   - Configure permissions:
     - **Models**: Leave empty for all models, or select specific models
     - **Endpoints**: Leave default for full access
   - Save
   - **Copy the Virtual Key** (starts with `sk-`)

4. **Configure Open WebUI**:
   - The Virtual Key is automatically used by Open WebUI if set in environment
   - Or configure in Open WebUI Settings → Connections

## Virtual Key Configuration

### Environment Variable

Virtual Key is stored in `.env` file:

```bash
VIRTUAL_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

**Note**: This file has restricted permissions (600) - only owner can read.

### Open WebUI Configuration

Open WebUI automatically uses Virtual Key from environment if available. The connection is configured automatically when you run `virtual-key.sh`.

If you need to configure manually:
1. Open Open WebUI Settings
2. Go to Connections
3. Add LiteLLM connection
4. Enter Virtual Key
5. Enter LiteLLM URL (usually `http://litellm:4000` for Docker network)

## Security Best Practices

1. **Never commit Virtual Key to git**
   - `.env` file should be in `.gitignore`
   - Virtual Key is sensitive information

2. **Use different Virtual Keys for different applications**
   - One for Open WebUI
   - One for Continue.dev
   - One for other integrations

3. **Restrict model access when possible**
   - If Open WebUI only needs specific models, limit Virtual Key to those models
   - Reduces risk if key is compromised

4. **Rotate keys periodically**
   - Create new Virtual Key
   - Update `.env` file
   - Restart containers
   - Revoke old key in LiteLLM Admin UI

5. **Monitor key usage**
   - Check LiteLLM Admin UI for key usage statistics
   - Set up alerts for unusual activity

## Troubleshooting

### Virtual Key Not Found Error

**Error**: "Virtual Key not found in .env" or "Virtual Key is required"

**When this happens:**
- After first run, Virtual Key becomes mandatory
- System checks for Virtual Key on startup (see `start_service.py`)
- If `FIRST_RUN=no` and `VIRTUAL_KEY` is empty, startup is blocked

**Solution**:
1. Check if Virtual Key exists in `.env` file:
   ```bash
   grep VIRTUAL_KEY .env
   ```
2. If missing, create Virtual Key:
   ```bash
   ./virtual-key.sh  # Linux/macOS
   virtual-key.bat   # Windows
   ```
3. Verify Virtual Key starts with `sk-`
4. Restart containers: `./stop.sh && ./start.sh`

**Note:** On first run (`FIRST_RUN=yes`), system allows Master Key as fallback. After Virtual Key is created, `FIRST_RUN` is set to `no` and Virtual Key becomes mandatory.

### Virtual Key Invalid Error

**Error**: "Invalid API key" or authentication failures

**Solution**:
1. Verify Virtual Key is correct in `.env` file
2. Check if Virtual Key exists in LiteLLM Admin UI
3. Verify Virtual Key hasn't been revoked
4. Check if Virtual Key has access to required models

### Models Not Appearing in Open WebUI

**Issue**: Models configured in LiteLLM but not visible in Open WebUI

**Possible causes**:
1. Virtual Key doesn't have access to models
2. Models are not marked as "Public" in LiteLLM Admin UI
3. Open WebUI connection not configured correctly

**Solution**:
1. In LiteLLM Admin UI, go to Models section
2. Enable "Public" checkbox for models you want to use
3. Verify Virtual Key has access to those models
4. Check Open WebUI connection settings

### Cannot Create Virtual Key

**Issue**: Script fails to create Virtual Key

**Solution**:
1. Verify containers are running: `docker compose ps`
2. Check LiteLLM is accessible: `curl http://localhost:4000/health`
3. Verify Master Key is correct in `.env` file
4. Try manual creation in LiteLLM Admin UI
5. Check logs: `docker compose logs litellm`

## Advanced Usage

### Multiple Virtual Keys

You can create multiple Virtual Keys for different purposes:

1. **Open WebUI Key**: Full access to all models
2. **Continue.dev Key**: Limited to specific models
3. **API Key**: For external applications

Each key can have different permissions and model access.

### Team-Based Access

Virtual Keys can be associated with teams for better organization:

1. Create teams for different user groups
2. Assign Virtual Keys to teams
3. Limit team access to specific models
4. Track usage per team

### Model Restrictions

To restrict Virtual Key to specific models:

1. In LiteLLM Admin UI, edit Virtual Key
2. In "Models" field, select specific models
3. Save changes
4. Virtual Key will only work with selected models

## Related Documentation

- [Getting Started Guide](../getting-started.md) - Initial setup including Virtual Key creation
- [Security Guide](../security.md) - Security best practices and Virtual Key security
- [Troubleshooting Guide](../troubleshooting.md) - Common issues and solutions
- [Continue.dev Integration](../integrations/continue-dev.md) - Using Virtual Key with Continue.dev

