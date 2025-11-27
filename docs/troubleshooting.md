# Troubleshooting Guide

## Models don't appear in Open WebUI?

1. Make sure models are configured in LiteLLM Admin UI (http://localhost:4000/ui)
2. Models should appear automatically - no restart needed
3. If models still don't appear, check:
   - Models are properly saved in LiteLLM Admin UI
   - Providers have valid API keys
   - Try refreshing Open WebUI page
   - As last resort: `docker compose restart litellm`

## Common Error Messages

### "Virtual Key not found" or "Virtual Key is required"

**Error message:**
```
❌ Virtual Key not found in .env
Virtual Key is required for Open WebUI to work properly
Master Key should not be used directly for security reasons
```

**Cause:**
- Virtual Key is missing from `.env` file
- This happens after first run (Virtual Key becomes mandatory)

**Solution:**
1. Create Virtual Key:
   ```bash
   # Linux/macOS
   ./virtual-key.sh
   
   # Windows
   virtual-key.bat
   ```
2. Virtual Key will be saved to `.env` automatically
3. Restart containers: `./stop.sh && ./start.sh`

**Note:** On first run, system allows Master Key as fallback. After first run, Virtual Key is required.

### "master key invalid" error?

**Error message:**
```
master key invalid
```

**Cause:**
- `LITELLM_MASTER_KEY` in `.env` doesn't start with `sk-`
- Master Key was changed but containers weren't restarted
- Master Key format is incorrect

**Solution:**
1. Check `.env` file:
   ```bash
   grep LITELLM_MASTER_KEY .env
   ```
2. Master Key must start with `sk-` (e.g., `sk-1234567890abcdef...`)
3. If incorrect, re-run setup: `./setup.sh`
4. Restart containers: `./stop.sh && ./start.sh`

### Port Conflicts

**Error message:**
```
Error: bind: address already in use
Port XXXX is already in use
```

**Cause:**
- Another service is using the configured port
- Previous containers are still running

**Solution:**
1. **Find what's using the port:**
   ```bash
   # Linux/macOS
   sudo lsof -i :PORT
   # Or
   sudo netstat -tulpn | grep :PORT
   
   # Windows
   netstat -ano | findstr :PORT
   ```

2. **Stop conflicting service or use different port:**
   - Re-run setup and choose different ports
   - Or use random high ports (49152-65535) for better security

3. **Check for old containers:**
   ```bash
   docker compose ps
   docker compose down  # Stop all containers
   ```

See [Port Configuration](configuration.md#port-conflicts-troubleshooting) for more details.

## Containers won't start?

**Error message:**
```
Failed to start containers
Some containers failed to start
```

**Possible causes:**
1. Virtual Key missing (after first run)
2. Port conflicts
3. Docker daemon not running
4. Configuration errors

**Solution:**
1. **Check container status:**
   ```bash
   docker compose ps
   ```

2. **View logs for failed containers:**
   ```bash
   docker compose logs
   # Or specific service
   docker compose logs litellm
   docker compose logs open-webui
   ```

3. **Check for Virtual Key (if not first run):**
   ```bash
   grep VIRTUAL_KEY .env
   # If missing, create it: ./virtual-key.sh
   ```

4. **Full restart:**
   ```bash
   docker compose down
   docker compose up -d
   ```

## Healthchecks and Startup Time

**Important:** Containers start quickly, but become ready for use after healthchecks pass. Understanding this process helps avoid confusion.

### Startup Process

1. **Containers start immediately** (30-60 seconds)
   - Docker Compose starts all containers
   - Containers begin initialization

2. **Healthchecks begin** (after start_period)
   - LiteLLM: `start_period: 40s` - healthcheck starts after 40 seconds (allows container to initialize before health checks begin)
   - PostgreSQL: healthcheck starts immediately
   - System waits for containers to become healthy
   - **Note:** `start_period: 40s` is the current value (was 600s in earlier versions, reduced for faster startup detection)

3. **LiteLLM requires time for Prisma migrations**
   - Prisma database migrations can take 1-5 minutes
   - This happens during container startup
   - Healthcheck waits for migrations to complete

4. **System automatically waits for readiness**
   - When using `./start.sh`, system waits up to 5 minutes (`--wait-timeout 300`)
   - System checks health status of all containers
   - Only reports success when all containers are healthy

### Expected Timeline

**First startup (with Prisma migrations):**
- **Container start:** 30-60 seconds
- **Healthcheck start period:** 40 seconds (LiteLLM)
- **Prisma migrations:** 10-30 seconds (45 migrations applied on first run)
- **Total ready time:** 1-2 minutes (typical)

**Subsequent startups (no migrations):**
- **Container start:** 30-60 seconds
- **Healthcheck start period:** 40 seconds (LiteLLM)
- **No Prisma migrations:** Database already initialized
- **Total ready time:** 1-1.5 minutes (typical)

**Note:** 
- First startup includes Prisma database migrations (45 migrations on clean install)
- Migrations typically take 10-30 seconds on first run
- Subsequent startups are faster as migrations are already applied
- Actual time may vary based on system performance and database state

### Checking Container Status

```bash
# Check container status and health
docker compose ps

# Expected output when ready:
# NAME                STATUS          HEALTH
# litellm-proxy       Up 2 minutes    healthy
# litellm-postgres    Up 2 minutes    healthy
# open-webui          Up 2 minutes    healthy
```

**Health status meanings:**
- `healthy` - Container is ready and passing healthchecks
- `starting` - Container is starting, healthcheck not yet passed
- `unhealthy` - Container is running but healthcheck is failing
- `(no healthcheck)` - Container doesn't have healthcheck (e.g., nginx)

### Troubleshooting Slow Startup

**If containers take longer than expected:**

1. **Check LiteLLM logs for Prisma migrations:**
   ```bash
   docker compose logs litellm | grep -i prisma
   docker compose logs litellm | grep -i migration
   ```

2. **Check database connection:**
   ```bash
   docker compose logs litellm | grep -i database
   docker compose logs postgres | tail -20
   ```

3. **Verify healthcheck configuration:**
   ```bash
   # Check healthcheck settings in docker-compose.yml
   grep -A 5 "healthcheck:" docker-compose.yml
   ```

4. **Wait for healthchecks:**
   - System automatically waits up to 5 minutes
   - Don't interrupt the startup process
   - Check status with `docker compose ps`

**Related:** [Getting Started - Step 2](getting-started.md#step-2-start-the-system)

```bash
# Check logs
docker compose logs

# Full restart
docker compose down
docker compose up -d
```

## PostgreSQL won't connect?

If password was changed, remove the volume:
```bash
docker compose down -v
docker compose up -d
```

## Memory Issues / Out of Memory (OOM) Errors?

**Check current memory usage:**
```bash
# Check container memory usage
docker stats --no-stream

# Check system memory
free -h

# Check for OOM kills
dmesg | grep -i "out of memory"
journalctl -k | grep -i "out of memory"
```

**Current memory usage** (measured, idle, based on Medium VPS profile):
- `litellm`: ~1.177 GiB (with 2 workers)
  - Base process: ~300-320MB
  - Per worker: ~460MB
- `open-webui`: ~602MB
- `postgres`: ~48MB (idle, can grow with usage)
- `nginx`: ~5-6MB
- **Note**: Small VPS uses 1 worker (LiteLLM: ~426.5MB), PostgreSQL: ~27MB, Open WebUI: ~603MB

**If containers are being killed due to memory issues:**

1. **Check actual usage**:
   ```bash
   docker stats --no-stream
   ```

2. **If system is running out of memory**:
   - Consider upgrading to a larger VPS (Medium VPS recommended for 4GB systems)
   - Reduce number of LiteLLM workers (edit `docker-compose.override.yml`, change `--num_workers`)
   - Monitor with: `docker stats` and `free -h`

3. **For Small VPS (2GB) users**:
   - ⚠️ Small VPS profile actually uses ~2.3-2.5GB on typical Linux distributions, exceeding 2GB by 15-25%
   - **Recommendations**:
     - **Best option**: Upgrade to Medium VPS (4GB) for safety ⭐
     - **Alternative 1**: Use lightweight Linux distribution (Alpine, Debian minimal, Ubuntu Server minimal) to reduce system overhead from ~1.2GB to ~0.7GB, bringing total to ~2.0GB (fits in 2GB, tight but feasible)
     - **Alternative 2**: If you must use 2GB with typical Linux, consider reducing to 1 worker (but performance will be limited)

**Memory usage details:**
- Each LiteLLM worker uses ~460MB RAM (measured, not estimated)
- LiteLLM base process: ~300-320MB (main process, dependencies)
- Open WebUI: ~600-603MB (varies by profile)
- PostgreSQL: ~20-60MB (idle, varies by profile: ~27MB for Small, ~48MB for Medium/Large)
- Nginx: ~5-6MB (very lightweight)
- Docker overhead: ~200MB (container runtime)
- System overhead: ~1.2GB (typical Linux) or ~0.7GB (lightweight distro)
- See [System Requirements - Resource Profiles](system-requirements.md#resource-profiles) for full breakdown

## HTTP Error Codes

When making API requests, you may encounter HTTP error codes. Here's what they mean and how to fix them:

**Note:** LiteLLM uses OpenAI-compatible error format and exception mapping. Errors from different providers are mapped to standard OpenAI error types. The error response format follows OpenAI API structure:

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": "error_code",
    "param": "parameter_name"  // Optional, indicates which parameter caused the error
  }
}
```

**LiteLLM Exception Types** (from [LiteLLM Exception Mapping](https://docs.litellm.ai/docs/exception_mapping)):
- `BadRequestError` (400) - Invalid request parameters
- `AuthenticationError` (401) - Authentication issues
- `UnsupportedParamsError` (400) - Unsupported parameters
- `ContextWindowExceededError` (400) - Context window exceeded
- `ContentPolicyViolationError` (400) - Content policy violation
- `ImageFetchError` (400) - Image processing errors

**Related:** 
- [LiteLLM Exception Mapping](https://docs.litellm.ai/docs/exception_mapping)
- [OpenAI Error Codes](https://platform.openai.com/docs/guides/error-codes)

### 401 Unauthorized

**Error message:**
```
401 Unauthorized
{
  "error": {
    "message": "Invalid API key",
    "type": "authentication_error",
    "code": "invalid_api_key"
  }
}
```

**Note:** LiteLLM uses OpenAI-compatible error format. The exact format may vary, but typically includes `message`, `type`, and `code` fields.

**Causes:**
- API key is missing or incorrect
- Virtual Key not set in `.env`
- Master Key format is invalid (doesn't start with `sk-`)
- Key was changed but containers weren't restarted

**Solutions:**
1. **Check API key:**
   ```bash
   grep VIRTUAL_KEY .env
   # Or
   grep LITELLM_MASTER_KEY .env
   ```

2. **Verify key format:**
   - Master Key must start with `sk-`
   - Virtual Key can be any string (typically starts with `sk-`)

3. **Create Virtual Key (if missing):**
   ```bash
   ./virtual-key.sh  # Linux/macOS
   virtual-key.bat   # Windows
   ```

4. **Restart containers:**
   ```bash
   ./stop.sh && ./start.sh
   ```

**Related:** [Virtual Key Guide](configuration/virtual-key.md)

### 403 Forbidden

**Error message:**
```
403 Forbidden
{
  "error": {
    "message": "Access denied",
    "type": "permission_error",
    "code": "access_denied"
  }
}
```

**Note:** LiteLLM uses OpenAI-compatible error format. Error details may vary based on specific permission issues.

**Causes:**
- Virtual Key doesn't have permission for requested endpoint
- Master Key required but Virtual Key provided
- Budget limit exceeded

**Solutions:**
1. **Check Virtual Key permissions:**
   - Access LiteLLM Admin UI: `http://localhost:PORT/ui`
   - Go to Virtual Keys section
   - Verify key has required permissions

2. **Check budget:**
   - Verify budget profile in `.env`: `BUDGET_PROFILE=test|prod|unlimited`
   - Check budget usage in LiteLLM Admin UI

3. **Use Master Key (if admin operation):**
   - Some admin operations require Master Key
   - ⚠️ Never use Master Key in client applications

### 404 Not Found

**Error message:**
```
404 Not Found
{
  "error": {
    "message": "Model not found",
    "type": "invalid_request_error",
    "code": "model_not_found",
    "param": "model"
  }
}
```

**Note:** LiteLLM uses OpenAI-compatible error format. The `param` field indicates which parameter caused the error.

**Causes:**
- Model ID is incorrect
- Model not configured in LiteLLM Admin UI
- Provider not configured or API key invalid
- Endpoint URL is incorrect

**Solutions:**
1. **Verify model exists:**
   ```bash
   curl http://localhost:PORT/api/litellm/v1/models \
     -H "Authorization: Bearer YOUR_VIRTUAL_KEY"
   ```

2. **Check model configuration:**
   - Access LiteLLM Admin UI: `http://localhost:PORT/ui`
   - Go to Models section
   - Verify model is configured and saved

3. **Check provider:**
   - Verify provider API key is valid
   - Check provider is configured in LiteLLM Admin UI

4. **Verify endpoint URL:**
   - With Nginx: `http://localhost:PORT/api/litellm/v1/...`
   - Without Nginx: `http://localhost:4000/v1/...`

**Related:** [Getting Started - Model IDs](getting-started.md#step-33-add-models)

### 429 Too Many Requests

**Error message:**
```
429 Too Many Requests
{
  "error": {
    "message": "Rate limit exceeded",
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded"
  }
}
```

**Note:** LiteLLM uses OpenAI-compatible error format. Rate limit errors may include `Retry-After` header indicating when to retry.

**Causes:**
- Too many requests in short time
- Provider rate limit exceeded
- Budget limit reached

**Solutions:**
1. **Implement exponential backoff:**
   ```python
   import time
   import random
   
   def retry_with_backoff(max_retries=3):
       for attempt in range(max_retries):
           try:
               # Make request
               return response
           except HTTPError as e:
               if e.response.status_code == 429:
                   wait_time = (2 ** attempt) + random.uniform(0, 1)
                   time.sleep(wait_time)
                   continue
               raise
   ```

2. **Check budget:**
   - Verify budget profile: `BUDGET_PROFILE=test|prod|unlimited`
   - Check usage in LiteLLM Admin UI

3. **Reduce request frequency:**
   - Implement request queuing
   - Batch requests when possible

4. **Check provider limits:**
   - Each provider has its own rate limits
   - Check provider documentation for limits

**Related:** [API for Agents - Rate Limits](integrations/api-for-agents.md#rate-limits)

### Rate Limits and Retry Policies

**Important:** LiteLLM automatically handles rate limit errors (429) with retry policies. Understanding how this works is crucial for troubleshooting.

#### How Retry Policies Work

When LiteLLM receives a 429 (Too Many Requests) error:

1. **LiteLLM does NOT return error immediately** - The client/agent continues waiting
2. **LiteLLM reads Retry-After header** - Automatically extracts wait time from 429 response
3. **Waits for Retry-After period** - Usually 60 seconds for Anthropic, or uses exponential backoff if header not present
4. **Retries request automatically** - Up to 3 retries (configurable via `LITELLM_NUM_RETRIES`)
5. **Only returns error after ALL retries fail** - If any retry succeeds, agent gets successful response (no error shown)

**Key Point:** Your agent/client receives a response, not an error, if any retry succeeds. This means:
- Requests may take longer than expected (due to retry delays)
- You may not see 429 errors even when rate limits are hit (retries handle it automatically)
- Total wait time depends on Retry-After values and number of retries

#### Configuration

Retry settings are configured in `config.yaml` and apply to all models (including UI-configured models):

```yaml
router_settings:
  max_retries: 3  # Number of retries for failed requests
  timeout: 600    # Request timeout: 10 minutes (allows retries with delays)
  retry_after: 120  # Base delay in seconds (used if Retry-After header not present)
```

**Important:** 
- `retry_after` is set to **120 seconds (2 minutes)** to allow rate limits to fully reset between retries
- This is especially important for Anthropic API Tier 1 (50k ITPM limit) - 120 seconds gives enough time for the token limit to fully reset
- LiteLLM automatically uses `Retry-After` header from 429 responses when available (usually 60 seconds for Anthropic)
- If `Retry-After` header is not present, LiteLLM uses `retry_after` value (120 seconds) or exponential backoff

#### Retry-After Header

- **Anthropic:** Usually 60 seconds (allows rate limit reset)
- **Other providers:** Varies by provider
- **If not present:** Uses exponential backoff: `base_delay * (2 ^ retry_count)`

**Related:** [Configuration Guide - Retry Policies](configuration.md#retry-policies)

### Practical Limitations of Anthropic API Tier 1

**⚠️ Important for beginners:** Anthropic API Tier 1 has strict rate limits that make work possible but not comfortable.

#### What is Tier 1?

Anthropic API Tier 1 is the default tier for new accounts. It has:
- **Rate limits:** 50,000 input tokens per minute (ITPM)
- **Strict enforcement:** Rate limits are actively enforced
- **Retry delays:** Usually 60 seconds when limit is hit

#### Practical Limitations

**Tier 1 makes work possible, but not comfortable:**

1. **Rate limits are restrictive:**
   - Frequent 429 errors during active use
   - Long wait times (60+ seconds) when limits are hit
   - Automatic retries help, but requests take longer

2. **System prompts help, but don't guarantee compliance:**
   - System prompts can guide model behavior
   - However, models may not always follow instructions exactly
   - User must actively manage context and conversation flow

3. **Context management is critical:**
   - User must actively manage conversation context
   - Context summary feature is **critically important** for Tier 1
   - Without proper context management, you'll hit rate limits more often

4. **For comfortable work, Tier 2+ is recommended:**
   - Tier 2+ has higher rate limits
   - Less frequent rate limit errors
   - Better experience for active AI assistant use

#### Recommendations

- **For testing/learning:** Tier 1 is sufficient
- **For active development:** Consider upgrading to Tier 2+
- **Use context summary:** Critical feature for managing long conversations
- **Monitor usage:** Check LiteLLM Admin UI for rate limit patterns
- **Understand retry behavior:** Requests may take longer due to automatic retries

**Note:** This information is based on practical experience with Anthropic API Tier 1. Rate limits and behavior may vary. Check [Anthropic API documentation](https://docs.anthropic.com/claude/docs/rate-limits) for current limits.

### 500 Internal Server Error

**Error message:**
```
500 Internal Server Error
{
  "error": {
    "message": "Internal server error",
    "type": "server_error",
    "code": "internal_error"
  }
}
```

**Note:** LiteLLM uses OpenAI-compatible error format. Internal errors may have varying details depending on the root cause.

**Causes:**
- LiteLLM service error
- Database connection issue
- Provider API error
- Configuration error

**Solutions:**
1. **Check LiteLLM logs:**
   ```bash
   docker compose logs litellm | tail -50
   ```

2. **Check database:**
   ```bash
   docker compose logs postgres | tail -50
   docker compose ps postgres  # Verify container is healthy
   ```

3. **Check configuration:**
   ```bash
   # Verify .env file
   cat .env | grep -v "^#"
   
   # Verify config.yaml
   cat config.yaml
   ```

4. **Restart services:**
   ```bash
   docker compose restart litellm
   # Or full restart
   ./stop.sh && ./start.sh
   ```

### 502 Bad Gateway

**Error message:**
```
502 Bad Gateway
```

**Causes:**
- Nginx can't reach LiteLLM service
- LiteLLM container is down or unhealthy
- Network issue between containers

**Solutions:**
1. **Check LiteLLM container:**
   ```bash
   docker compose ps litellm
   docker compose logs litellm | tail -50
   ```

2. **Check health:**
   ```bash
   # Health check endpoint
   curl http://localhost:4000/health/liveliness
   # Or from inside container
   docker exec litellm-proxy wget -qO- http://localhost:4000/health/liveliness
   ```

3. **Check network:**
   ```bash
   docker network inspect ai-gateway_litellm-network
   ```

4. **Restart LiteLLM:**
   ```bash
   docker compose restart litellm
   ```

### 503 Service Unavailable

**Error message:**
```
503 Service Unavailable
```

**Causes:**
- Service is starting up
- Health check failed
- Container is restarting

**Solutions:**
1. **Wait for startup:**
   - Services need time to start (30-60 seconds)
   - Check container status: `docker compose ps`

2. **Check health:**
```bash
# Option 1: Direct grep (works everywhere)
docker compose ps --format json | grep -A 2 Health

# Option 2: Table format (more readable)
docker compose ps --format 'table {{.Name}}\t{{.Status}}' | grep -i health
```

3. **View logs:**
   ```bash
   docker compose logs SERVICE_NAME | tail -50
   ```

4. **If persistent:**
   ```bash
   # Full restart
   ./stop.sh && ./start.sh
   ```

## Diagnostic Commands

Use these commands to diagnose issues:

### Container Status

**Container Names:**
AI Gateway uses fixed container names for easy identification:
- `litellm-proxy` - LiteLLM API proxy and admin UI
- `litellm-postgres` - PostgreSQL database
- `open-webui` - Open WebUI web interface
- `litellm-nginx` - Nginx reverse proxy

**Docker Network:**
- Network name: `{project}_litellm-network` (e.g., `ai-gateway_litellm-network`)
- Network type: `bridge`
- All containers are connected to this isolated network

**Check all containers:**
```bash
docker compose ps
```

**Expected output:**
```
NAME                STATUS          HEALTH
litellm-proxy       Up 2 minutes    healthy
litellm-postgres    Up 2 minutes    healthy
open-webui          Up 2 minutes    healthy
litellm-nginx       Up 2 minutes    (no healthcheck)
```

**Check specific container:**
```bash
docker compose ps SERVICE_NAME
```

**Check health status:**
```bash
# Option 1: Direct grep (works everywhere)
docker compose ps --format json | grep -A 2 Health

# Option 2: Table format (more readable)
docker compose ps --format 'table {{.Name}}\t{{.Status}}' | grep -i health
```

### View Logs

**All services:**
```bash
docker compose logs
```

**Specific service:**
```bash
docker compose logs SERVICE_NAME
```

**Follow logs (real-time):**
```bash
docker compose logs -f SERVICE_NAME
```

**Last N lines:**
```bash
docker compose logs --tail=50 SERVICE_NAME
```

**Filter by keyword:**
```bash
docker compose logs SERVICE_NAME | grep -i error
docker compose logs SERVICE_NAME | grep -i "connection"
```

### Network Diagnostics

**Check Docker network:**
```bash
docker network inspect ai-gateway_litellm-network
```

**Check port mappings:**
```bash
docker compose ps
# Or
docker compose port SERVICE_NAME INTERNAL_PORT
```

**Test connectivity (from host):**
```bash
# Test LiteLLM API
curl http://localhost:PORT/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY"

# Test health endpoint
curl http://localhost:PORT/health/liveliness
```

**Test connectivity (from container):**
```bash
# Test LiteLLM from inside container
docker exec litellm-proxy wget -qO- http://localhost:4000/health/liveliness

# Test PostgreSQL from inside container
docker exec litellm-proxy ping postgres
```

### Resource Usage

**Container resource usage:**
```bash
docker stats --no-stream
```

**System memory:**
```bash
free -h
```

**System disk:**
```bash
df -h
```

**Container disk usage:**
```bash
docker system df
```

### Configuration Verification

**Check .env file:**
```bash
# View all variables (excluding comments)
cat .env | grep -v "^#" | grep -v "^$"

# Check specific variable
grep VARIABLE_NAME .env

# Check required variables
grep -E "LITELLM_MASTER_KEY|VIRTUAL_KEY|POSTGRES_" .env
```

**Check config.yaml:**
```bash
cat config.yaml
```

**Check docker-compose.override.yml:**
```bash
cat docker-compose.override.yml
```

**Verify file permissions:**
```bash
stat -c "%a %n" .env config.yaml docker-compose.override.yml
# Expected:
# .env: 600 (contains sensitive data)
# config.yaml: 644 (does not contain sensitive data, API keys are in .env)
# docker-compose.override.yml: 600 (contains sensitive data)
```

### API Testing

**List available models:**
```bash
curl http://localhost:PORT/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" | jq
```

**Test chat completion:**
```bash
curl http://localhost:PORT/api/litellm/v1/chat/completions \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "messages": [{"role": "user", "content": "Hello"}]
  }' | jq
```

**Check health:**
```bash
# LiteLLM health
curl http://localhost:PORT/health/liveliness

# Or from inside container
docker exec litellm-proxy wget -qO- http://localhost:4000/health/liveliness
```

## Log Interpretation

Understanding logs helps diagnose issues quickly:

### LiteLLM Logs

**Note:** LiteLLM uses ANSI color codes in logs (e.g., `[92m...` for DEBUG, `[0m` for reset). When viewing logs in terminal, colors are rendered automatically. When viewing in files or non-color terminals, you may see these codes as text.

**Normal startup:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4000
```

**With color codes (raw format):**
```
[92m12:06:36 - LiteLLM Proxy:DEBUG[0m Starting server...
[92m12:06:36 - LiteLLM Proxy:INFO[0m Application startup complete.
```

**Database connection:**
```
INFO:     Connecting to database...
INFO:     Database connection established
```

**Error patterns:**

**Database connection error:**
```
ERROR:     Could not connect to database
ERROR:     Connection refused
```
**Solution:** Check PostgreSQL container is running and healthy.

**Invalid API key:**
```
ERROR:     Invalid API key for provider: anthropic
ERROR:     Authentication failed
```
**Solution:** Verify API key in LiteLLM Admin UI or `.env` file.

**Model not found:**
```
ERROR:     Model not found: claude-sonnet-4-5
ERROR:     Model configuration missing
```
**Solution:** Configure model in LiteLLM Admin UI.

**Rate limit:**
```
ERROR:     Rate limit exceeded
ERROR:     429 Too Many Requests
```
**Solution:** Implement exponential backoff, check budget limits.

### PostgreSQL Logs

**Normal startup:**
```
database system is ready to accept connections
```

**Connection errors:**
```
FATAL:  password authentication failed
FATAL:  database "litellm" does not exist
```
**Solution:** Check `POSTGRES_PASSWORD` and `POSTGRES_DB` in `.env`.

### Open WebUI Logs

**Normal startup:**
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Connection errors:**
```
ERROR:     Could not connect to LiteLLM API
ERROR:     Connection refused
```
**Solution:** Check LiteLLM container is running and Virtual Key is set.

### Nginx Logs

**Normal operation:**
```
[INFO] 127.0.0.1 - - "GET / HTTP/1.1" 200
```

**Error patterns:**

**502 Bad Gateway:**
```
[ERROR] upstream connect failed
[ERROR] connection refused
```
**Solution:** Check LiteLLM container is running and healthy.

**404 Not Found:**
```
[ERROR] 404 Not Found
```
**Solution:** Check URL path is correct (e.g., `/api/litellm/v1/...`).

### Common Log Patterns

**Container restart loop:**
```
ERROR: Container exited with code 1
INFO:  Container restarting...
ERROR: Container exited with code 1
```
**Solution:** Check logs for specific error, check configuration.

**Health check failures:**
```
WARNING: Health check failed
WARNING: Container unhealthy
```
**Solution:** Check service logs, verify health check endpoint.

**Port already in use:**
```
ERROR: bind: address already in use
ERROR: Port 4000 is already in use
```
**Solution:** Find and stop conflicting service, or use different port.

## Additional Error Messages

### Docker Errors

**"Cannot connect to Docker daemon":**
```bash
# Check Docker is running
docker ps

# Start Docker (Linux)
sudo systemctl start docker

# Start Docker (macOS)
open -a Docker
```

**"Permission denied":**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and log back in
```

**"No space left on device":**
```bash
# Check disk space
df -h

# Clean up Docker
docker system prune -a
```

### Configuration Errors

**"File not found: .env":**
```bash
# Run setup to create .env
./setup.sh
# Or
./ai-gateway setup
```

**"Invalid port range":**
- Ports must be between 1024-65535
- Check port values in `.env`

**"Invalid budget profile":**
- Must be: `test`, `prod`, or `unlimited`
- Check `BUDGET_PROFILE` in `.env`

### API Errors

**"Model timeout":**
- Request took too long (>10 minutes default)
- Check provider API status
- Check network connectivity

**"Invalid request format":**
- Verify JSON format is correct
- Check required fields are present
- See [API for Agents](integrations/api-for-agents.md) for examples

**"Provider API error":**
- Check provider API key is valid
- Check provider service status
- Verify model ID is correct

## Docker Daemon Not Starting Automatically

**Important:** Docker daemon may not start automatically after system reboot. AI Gateway includes automatic detection and startup functionality.

### Automatic Detection and Startup

AI Gateway automatically detects and attempts to start Docker daemon when needed:

1. **Automatic Detection:**
   - System checks if Docker daemon is running before starting containers
   - Detects rootless Docker vs regular Docker
   - Checks for systemd user services

2. **Automatic Startup (if available):**
   - **Rootless Docker with systemd:** Uses `systemctl --user start docker`
   - **Rootless Docker without systemd:** Attempts to start `dockerd-rootless.sh` in background
   - **Regular Docker:** Prompts for sudo access to start system service

3. **Integration with systemd user services:**
   - If systemd is available, uses systemd user service for rootless Docker
   - Service is automatically enabled for startup on boot (if configured)
   - Works seamlessly with systemd user services

### Manual Startup Instructions

If automatic startup doesn't work, start Docker daemon manually:

**For Rootless Docker (with systemd):**
```bash
# Start Docker daemon
systemctl --user start docker

# Enable automatic startup on boot
systemctl --user enable docker

# Check status
systemctl --user status docker
```

**For Rootless Docker (without systemd):**
```bash
# Start Docker daemon manually
dockerd-rootless.sh

# Or with environment variables
XDG_RUNTIME_DIR=~/.docker/run DOCKER_HOST=unix://~/.docker/run/docker.sock dockerd-rootless.sh
```

**For Regular Docker (system-wide):**
```bash
# Start Docker daemon (requires sudo)
sudo systemctl start docker

# Enable automatic startup on boot
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### Troubleshooting

**Docker daemon not starting automatically:**

1. **Check if Docker is installed:**
   ```bash
   docker --version
   ```

2. **For rootless Docker, check initialization:**
   ```bash
   # Check if rootless Docker is initialized
   dockerd-rootless-setuptool.sh install
   ```

3. **Check systemd user service (for rootless Docker):**
   ```bash
   # Check if service exists
   systemctl --user list-unit-files | grep docker
   
   # Check service status
   systemctl --user status docker
   
   # Enable lingering (allows user services without login)
   loginctl enable-linger $USER
   ```

4. **Check Docker socket:**
   ```bash
   # For rootless Docker
   ls -la ~/.docker/run/docker.sock
   
   # For regular Docker
   ls -la /var/run/docker.sock
   ```

5. **View Docker daemon logs:**
   ```bash
   # For rootless Docker with systemd
   journalctl --user -u docker -f
   
   # For regular Docker
   sudo journalctl -u docker -f
   ```

**Common Issues:**

- **"Cannot connect to Docker daemon":** Docker daemon is not running - start it manually (see instructions above)
- **"Permission denied":** Check Docker socket permissions or use rootless Docker
- **"systemd user service not found":** Initialize rootless Docker: `dockerd-rootless-setuptool.sh install`
- **"Docker daemon not starting after reboot":** Enable systemd user service: `systemctl --user enable docker` and `loginctl enable-linger $USER`

**Related:** [Installation Guide - Docker Access](installation.md#docker-access), [Systemd Service](administration/systemd.md)

## Step-by-Step Diagnostic Process

When troubleshooting, follow this process:

1. **Check container status:**
   ```bash
   docker compose ps
   ```

2. **View logs for errors:**
   ```bash
   docker compose logs | grep -i error
   ```

3. **Check specific service:**
   ```bash
   docker compose logs SERVICE_NAME | tail -50
   ```

4. **Verify configuration:**
   ```bash
   grep VARIABLE_NAME .env
   ```

5. **Test connectivity:**
   ```bash
   curl http://localhost:PORT/health/liveliness
   ```

6. **Check resource usage:**
   ```bash
   docker stats --no-stream
   free -h
   ```

7. **Restart if needed:**
   ```bash
   docker compose restart SERVICE_NAME
   # Or full restart
   ./stop.sh && ./start.sh
   ```

## Common Configuration Errors

**Important lesson:** Configuration errors may cause problems that seem unrelated. Always verify your configuration.

### Error: Specifying `openai` as Provider for All Models

**Problem:** Specifying `provider: openai` for all models in Continue.dev configuration.

**Why it's wrong:**
- LiteLLM is OpenAI-compatible API, but internally uses real provider names
- Claude models need `provider: anthropic` for proper tool use support
- Azure models need `provider: azure` for Azure-specific features
- Using wrong provider may cause tool-call-filter errors or missing features

**Correct solution:**
- ✅ **Let the setup script automatically determine provider** (recommended)
  - Run `./ai-gateway continue-dev`
  - Script automatically detects provider based on model ID
- ✅ **Or manually specify the real provider name:**
  - Claude models: `provider: anthropic`
  - Azure models: `provider: azure`
  - OpenAI models: `provider: openai`

**How provider is determined:**
- Models starting with `claude-`: `provider: anthropic`
- Models `gpt-5-mini` or starting with `azure/`: `provider: azure`
- Other models: `provider: openai`

**Example of correct configuration:**

```yaml
models:
  - title: Claude Sonnet 4.5
    provider: anthropic  # ✅ Correct - real provider name
    model: claude-sonnet-4-5
    apiBase: http://localhost:PORT/api/litellm/v1
    
  - title: GPT-4o
    provider: openai  # ✅ Correct - real provider name
    model: gpt-4o
    apiBase: http://localhost:PORT/api/litellm/v1
```

**Example of incorrect configuration:**

```yaml
models:
  - title: Claude Sonnet 4.5
    provider: openai  # ❌ Wrong - should be 'anthropic'
    model: claude-sonnet-4-5
    apiBase: http://localhost:PORT/api/litellm/v1
```

**Related:** [Continue.dev Integration - Correct Provider Configuration](integrations/continue-dev.md#correct-provider-configuration)

## Proxmox LXC Issues

**If you're trying to run AI Gateway in a Proxmox LXC container and encountering issues:**

### Common Errors

**"Permission denied" when initializing rootless Docker:**
```
Error: failed to start daemon: Error initializing network controller: error creating default "bridge" network: operation not permitted
```

**"Cannot connect to Docker daemon":**
```
Cannot connect to the Docker daemon at unix:///run/user/1000/docker.sock
```

**Kernel namespace errors:**
```
Error: failed to setup network: failed to create namespace: operation not permitted
```

### Why These Errors Occur

- **Unprivileged LXC containers** have kernel-level restrictions on user namespaces
- **Rootless Docker requires user namespaces** which are not reliably available in LXC
- **Even with proper configuration** (subuid/subgid, AppArmor), kernel may deny access

### Solution

**Use a full VM instead of an LXC container:**

1. **Create a new VM in Proxmox:**
   - Use any Linux distribution (Ubuntu, Debian, etc.)
   - Allocate sufficient resources (see [System Requirements](system-requirements.md))
   - Install Docker and Docker Compose

2. **Follow standard installation:**
   - Rootless Docker works reliably in VMs
   - Follow [Installation Guide](installation.md) as normal
   - No special configuration needed

**Why VM is better:**
- ✅ More reliable than privileged LXC containers
- ✅ Better isolation and security
- ✅ No kernel-level namespace restrictions
- ✅ Standard Docker/rootless Docker support

**Note:** If you must use LXC, privileged containers may work but are not recommended due to security concerns. VM is the recommended solution.

**Related:** [Installation Guide - Proxmox LXC](installation.md#proxmox-lxc-containers), [System Requirements - Proxmox LXC](system-requirements.md#proxmox-lxc-containers)

## Getting More Help

If you can't resolve the issue:

1. **Check documentation:**
   - [FAQ](FAQ.md) - Common questions
   - [Getting Started](getting-started.md) - Setup guide
   - [Configuration Guide](configuration.md) - Configuration details

2. **Collect diagnostic information:**
   ```bash
   # Container status
   docker compose ps > diagnostics.txt
   
   # Recent logs
   docker compose logs --tail=100 >> diagnostics.txt
   
   # Configuration (remove sensitive data)
   grep -v "KEY\|PASSWORD" .env >> diagnostics.txt
   ```

3. **Check GitHub issues:**
   - Search existing issues
   - Create new issue with diagnostic information

**Related:**
- [FAQ](FAQ.md) - More common questions
- [Configuration Guide](configuration.md) - Configuration details
- [API for Agents](integrations/api-for-agents.md) - API troubleshooting

