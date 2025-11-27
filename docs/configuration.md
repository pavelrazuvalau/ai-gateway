# Configuration Guide

## Quick Links

- **[Port Configuration](#port-configuration)** - Configure ports and network access
- **[Resource Profiles](#resource-profiles)** - RAM and CPU settings
- **[Budget Profiles](#budget-profiles)** - Spending limits
- **[Environment Variables Reference](#environment-variables-reference)** - Complete variable list
- **[Examples](examples/configuration-examples.md)** - Configuration examples

**Related Documentation:**
- [Getting Started](getting-started.md) - Initial setup
- [System Requirements](system-requirements.md) - Resource requirements
- [Security Guide](security.md) - Security configuration
- [Troubleshooting](troubleshooting.md) - Configuration issues

## Port Configuration

### Default Ports

| Service | Internal Port | External Port (with Nginx) | External Port (without Nginx) | Description |
|---------|--------------|---------------------------|-------------------------------|-------------|
| **Open WebUI** | 8080 | Via Nginx (root `/`) | 3000 | Web interface |
| **LiteLLM API** | 4000 | Via Nginx (`/api/litellm/v1/*`) | 4000 | API proxy |
| **LiteLLM UI** | 4000 | Separate port (configurable) | 4000 | Admin UI (`/ui` path) |
| **PostgreSQL** | 5432 | Not exposed | Not exposed | Database (internal only) |
| **Nginx** | 80 | Configurable (default: random high port) | N/A | Reverse proxy |

**Note:** Internal ports are used within Docker network. External ports are exposed to host system.

### Default Configuration (with Nginx - Enabled by Default)

**During setup, Nginx reverse proxy is enabled by default** (you can disable it if needed). This provides enhanced security by exposing only one external port:

- **Single External Port** (via Nginx):
  - **Open WebUI**: Available at root path `/` (e.g., `http://localhost:PORT/`)
  - **LiteLLM API**: Available at `/api/litellm/v1/*` (e.g., `http://localhost:PORT/api/litellm/v1/chat/completions`)
  - **All other services**: Closed to external access (PostgreSQL, LiteLLM UI remain internal)

- **LiteLLM UI**: Still accessible on separate port for local network configuration (optional, configurable during setup)

**Ports are configured when running `./ai-gateway setup` or `./setup.sh`** - Nginx reverse proxy is enabled by default (press Enter to accept, or type 'n' to disable).

**Note:** The internal nginx container provides HTTP only. For SSL/HTTPS support in production, see [External Nginx Configuration](nginx/README.md) in the `docs/` directory.

### Alternative Configuration (without Nginx)

If you disable Nginx during setup, services will be exposed on separate ports:
- **Open WebUI**: 3000 (external port, internal is 8080)
- **LiteLLM API**: 4000 (external port)
- **LiteLLM UI**: 4000/ui (same port as API)
- **PostgreSQL**: 5432 (internal only, never exposed)

### Finding Configured Ports

Ports are stored in `.env` file:
- `NGINX_HTTP_PORT` or `NGINX_PORT` - Nginx external port (if Nginx enabled)
- `LITELLM_EXTERNAL_PORT` - LiteLLM external port (for UI access)
- `WEBUI_EXTERNAL_PORT` - Open WebUI external port (if Nginx disabled)
- `POSTGRES_PORT` - PostgreSQL port (internal, usually 5432)

**Check ports:**
```bash
# View configured ports
grep -E "PORT|NGINX" .env

# Or view all port-related settings
cat .env | grep -i port
```

**View from Docker:**
```bash
# Show port mappings
docker compose ps

# Or inspect specific service
docker compose port nginx 80
docker compose port litellm 4000
```

### Port Conflicts Troubleshooting

If you see "port already in use" errors:

1. **Check what's using the port:**
   ```bash
   # Linux/macOS
   sudo lsof -i :PORT
   # Or
   sudo netstat -tulpn | grep :PORT
   
   # Windows
   netstat -ano | findstr :PORT
   ```

2. **Common conflicts:**
   - Port 80: Often used by system services (use random high port instead)
   - Port 3000: May be used by other web apps
   - Port 4000: May be used by other services
   - Port 5432: PostgreSQL may already be running

3. **Solutions:**
   - Use random high ports (49152-65535) for better security
   - Stop conflicting services
   - Re-run setup and choose different ports
   - Check `docker-compose.override.yml` for port mappings

See [Troubleshooting Guide](troubleshooting.md#port-conflicts) for more details.

## Resource Profiles

| Profile | RAM | CPU | Users | Description |
|---------|-----|-----|-------|-------------|
| **Local** | No limits | No limits | - | Local development |
| **Small VPS** | 2GB | 2 CPU | 1-2 | ⚠️ **Warning**: Actual usage ~2.3-2.5GB (exceeds 2GB by 15-25%)<br>💡 **Tip**: Use lightweight Linux (Alpine, Debian minimal, Ubuntu Server minimal) to reduce overhead to ~2.0GB |
| **Medium VPS** | 4GB | 4 CPU | 3-5 | ⭐ **Recommended** - Actual usage ~3.3GB |
| **Large VPS** | 8GB+ | 8 CPU | 10+ | For teams - Actual usage ~5.1GB |

**Note:** Memory usage is based on real measurements (2025-11-24). Each LiteLLM worker uses ~460MB RAM (measured, not estimated). 

**💡 For Small VPS (2GB) users:** Consider using a lightweight Linux distribution (Alpine Linux, Debian minimal, Ubuntu Server minimal) to reduce system overhead from ~1.2GB to ~0.7GB, bringing total usage to ~2.0GB (fits in 2GB, tight but feasible). See [System Requirements - Tips for Small VPS](system-requirements.md#-tips-for-small-vps-2gb-users) for details.

See [System Requirements - Resource Profiles](system-requirements.md#resource-profiles) for detailed breakdown.

## Budget Profiles

| Profile | Total Budget | Description |
|---------|--------------|-------------|
| **test** | $15/month | Test environment |
| **prod** | $200/month | Regular use |
| **unlimited** | $1000/month | No limits |

You can change the profile:
- In `.env`: `BUDGET_PROFILE=test|prod|unlimited`
- When starting: `./start.sh prod`

## Network Access

### Accessing from Local Network

By default, services are accessible from:
- **localhost** (127.0.0.1) - same machine
- **Local network** - other devices on same network

**Find your server IP address:**
```bash
# Linux/macOS
ip addr show | grep "inet " | grep -v 127.0.0.1
# Or
hostname -I

# Windows
ipconfig
```

**Access URLs from other devices:**
- Replace `localhost` with your server IP
- Example: `http://192.168.1.100:3000` instead of `http://localhost:3000`

### Firewall Configuration

If you can't access from other devices, check firewall:

**Linux (firewalld):**
```bash
# Check status
sudo firewall-cmd --list-all

# Allow ports (example for port 3000)
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

**Linux (ufw):**
```bash
# Allow ports
sudo ufw allow 3000/tcp
sudo ufw allow 4000/tcp
sudo ufw status
```

**Windows:**
- Open Windows Firewall settings
- Add inbound rule for required ports
- Or temporarily disable firewall for testing

**Which ports need to be open?**
- **With Nginx**: Only Nginx port (default: random high port, or configured port)
- **Without Nginx**: Open WebUI port (3000) and LiteLLM port (4000)
- **PostgreSQL**: Never expose (internal only)

**Security Note:**
- For production, use firewall to restrict access
- Consider VPN for remote access instead of exposing ports
- Use SSL/HTTPS for encrypted connections
- See [Security Guide](security.md) for production recommendations

## Memory Configuration

### Memory Usage

Memory usage is based on real measurements (2025-11-24). Current usage per service:

- **litellm**: ~1.177 GiB (with 2 workers, idle)
  - Base process: ~300-320MB (main process, dependencies)
  - Per worker: ~460MB (measured, not estimated)
  - Can grow during active requests (+200-400MB per worker)
- **open-webui**: ~600-603MB (varies by profile)
  - Small VPS: ~603MB
  - Medium/Large VPS: ~602MB
  - Can grow during active chat sessions (+100-200MB)
- **postgres**: ~20-60MB (idle, varies by profile)
  - Small VPS: ~27MB
  - Medium/Large VPS: ~48MB
  - Can grow during queries (+50-100MB)
- **nginx**: ~5-6MB (very lightweight)
  - Minimal overhead
- **Docker overhead**: ~200MB (container runtime)

**Note:** Memory limits via `deploy.resources` are not supported in rootless Docker. For production deployments, consider using system-level memory management or Docker Swarm mode if memory limits are required.

## Web Search Configuration

Open WebUI supports web search functionality that allows AI models to search the internet for real-time information. The web search configuration is automatically optimized based on your resource profile during setup.

### Supported Search Engines

The following search engines are supported (all require API keys):

| Engine | Description | API Key Required | Free Tier |
|--------|-------------|------------------|-----------|
| **tavily** | ⭐ **Recommended** - Optimized for AI/LLM use cases, better accuracy | `TAVILY_API_KEY` | Yes (1000 searches/month) |
| **google_pse** | Google Programmable Search Engine - Good accuracy | `GOOGLE_PSE_API_KEY` | Limited |
| **serper** | Good for technical queries | `SERPER_API_KEY` | Limited |
| **brave** | Good privacy features | `BRAVE_API_KEY` | Limited |
| **kagi** | Good results quality | `KAGI_API_KEY` | Paid only |

**Note:** The stack no longer bundles Playwright/web loader. Engines that only return URLs (e.g., `ddgs`) are not supported out-of-the-box. Use API-based providers that return extracted content.

### Configuration via Environment Variables

Web search settings can be configured in `.env` file:

```bash
# Web Search Engine (default: tavily)
WEB_SEARCH_ENGINE=tavily

# Tavily API Key (required if WEB_SEARCH_ENGINE=tavily)
# Get free API key at: https://tavily.com/
TAVILY_API_KEY=your-api-key-here

# Google PSE API Key (required if WEB_SEARCH_ENGINE=google_pse)
GOOGLE_PSE_API_KEY=your-api-key-here

# Serper API Key (required if WEB_SEARCH_ENGINE=serper)
SERPER_API_KEY=your-api-key-here

# Brave API Key (required if WEB_SEARCH_ENGINE=brave)
BRAVE_API_KEY=your-api-key-here

# Kagi API Key (required if WEB_SEARCH_ENGINE=kagi)
KAGI_API_KEY=your-api-key-here

# Concurrent requests (automatically set by profile, can override)
WEB_SEARCH_CONCURRENT_REQUESTS=1

# Number of search results to fetch (automatically set by profile, can override)
WEB_SEARCH_RESULT_COUNT=1
```

### Profile-Based Defaults

Web search settings are automatically optimized based on your resource profile:

| Profile | Concurrent Requests | Result Count | Notes |
|---------|-------------------|--------------|-------|
| **Small VPS** (2GB) | 1 | 1 | Minimal resource usage |
| **Medium VPS** (4GB) | 1 | 1 | Balanced performance |
| **Large VPS** (8GB+) | 2 | 3 | Higher throughput |
| **Desktop** | 3 | 4 | Maximum performance |

These defaults are set during setup and can be overridden in `.env` file.

### Setting Up Tavily (Recommended)

1. **Get API Key:**
   - Visit: https://tavily.com/
   - Sign up for a free account
   - Get your API key from the dashboard
   - Free tier: 1000 searches/month

2. **Configure in .env:**
   ```bash
   WEB_SEARCH_ENGINE=tavily
   TAVILY_API_KEY=your-tavily-api-key-here
   ```

3. **Update OpenWebUI Settings:**
   - Settings are automatically updated from environment variables on container start
   - If container is already running, restart it: `docker compose restart open-webui`
   - Or run setup again to update settings: `./ai-gateway setup`

### Setting Up Other Engines

For other search engines (Google PSE, Serper, Brave, Kagi):

1. **Get API Key** from the respective provider
2. **Set in .env:**
   ```bash
   WEB_SEARCH_ENGINE=google_pse  # or serper, brave, kagi
   GOOGLE_PSE_API_KEY=your-api-key-here  # or SERPER_API_KEY, BRAVE_API_KEY, KAGI_API_KEY
   ```
3. **Restart container** to apply changes: `docker compose restart open-webui`

### Advanced Configuration

#### Concurrent Requests

Controls how many search requests can run simultaneously. Higher values increase throughput but also increase CPU and memory usage.

```bash
# For low-resource systems (Small/Medium VPS)
WEB_SEARCH_CONCURRENT_REQUESTS=1

# For high-resource systems (Large VPS, Desktop)
WEB_SEARCH_CONCURRENT_REQUESTS=2  # or 3
```

#### Result Count

Number of search results to fetch per query. More results provide better context but increase API usage and processing time.

```bash
# Minimal results (faster, lower API usage)
WEB_SEARCH_RESULT_COUNT=1

# More results (better context, higher API usage)
WEB_SEARCH_RESULT_COUNT=3  # or 4
```

### Troubleshooting

**Web search not working:**

1. **Check API Key:**
   ```bash
   # Verify API key is set in .env
   grep -E "WEB_SEARCH_ENGINE|TAVILY_API_KEY" .env
   ```

2. **Check Container Environment:**
   ```bash
   # Verify environment variables are passed to container
   docker exec open-webui env | grep WEB_SEARCH
   ```

3. **Check OpenWebUI Settings:**
   - Open WebUI → Settings → Features
   - Verify web search is enabled
   - Check that engine matches your `.env` configuration

4. **Restart Container:**
   ```bash
   docker compose restart open-webui
   ```

**API Key Errors:**

- Verify API key is correct and active
- Check API key quota/limits (especially for free tiers)
- For Tavily: Ensure you haven't exceeded 1000 searches/month on free tier

**Settings Not Updating:**

- Settings are automatically synced from environment variables on container start
- If settings don't match `.env`, restart the container: `docker compose restart open-webui`
- Or run setup again: `./ai-gateway setup` (will update settings if container is running)

### How It Works

1. **Environment Variables** in `.env` are read during container startup
2. **OpenWebUI Database** is updated with settings from environment variables
3. **Settings Take Precedence:** Environment variables override UI settings
4. **Automatic Sync:** Settings are synced on container start (if `UPDATE_WEB_SEARCH_SETTINGS` flag is set)

The web search configuration is managed by `src/infrastructure/openwebui_db.py`, which updates the OpenWebUI database from environment variables.

## Retry Policies

LiteLLM automatically handles rate limit errors (429) with configurable retry policies. Understanding retry configuration is important for production deployments.

### How Retry Policies Work

When a request receives a 429 (Too Many Requests) error:

1. **LiteLLM does NOT return error immediately** - Client/agent continues waiting
2. **LiteLLM reads Retry-After header** - Automatically extracts wait time from 429 response
3. **Waits for Retry-After period** - Usually 60 seconds for Anthropic
4. **Retries request automatically** - Up to 3 retries (configurable)
5. **Only returns error after ALL retries fail** - If any retry succeeds, client gets successful response

**Key Point:** Your client receives a response, not an error, if any retry succeeds. This means requests may take longer than expected due to retry delays.

### Configuration in config.yaml

Retry settings are configured in `config.yaml` and apply to **all models** (including UI-configured models):

```yaml
router_settings:
  max_retries: 3  # Number of retries for failed requests
  timeout: 600    # Request timeout: 10 minutes (allows retries with delays)
  retry_after: 120  # Base delay in seconds (used if Retry-After header not present)
```

**Important:** 
- These `router_settings` apply to **all models**, including models configured via LiteLLM Admin UI. This ensures consistent retry behavior across all models.
- `retry_after` is set to **120 seconds (2 minutes)** to allow rate limits to fully reset between retries
- This is especially important for Anthropic API Tier 1 (50k ITPM limit) - 120 seconds gives enough time for the token limit to fully reset
- LiteLLM automatically uses `Retry-After` header from 429 responses when available (usually 60 seconds for Anthropic)
- If `Retry-After` header is not present, LiteLLM uses `retry_after` value (120 seconds) or exponential backoff

### Retry-After Header

- **Anthropic:** Usually 60 seconds (allows rate limit reset)
- **Other providers:** Varies by provider
- **If not present:** Uses exponential backoff: `base_delay * (2 ^ retry_count)`

### Environment Variables

Retry configuration can also be set via environment variables in `.env`:

```bash
# Number of retries (also set in config.yaml)
LITELLM_NUM_RETRIES=3

# Request timeout in seconds (10 minutes allows retries with delays)
LITELLM_TIMEOUT=600
```

**Note:** Settings in `config.yaml` take precedence. Environment variables are used as defaults.

### Understanding Retry Behavior

**What you see:**
- Requests may take longer than expected (due to retry delays)
- You may not see 429 errors even when rate limits are hit (retries handle it automatically)
- Total wait time depends on Retry-After values and number of retries

**What happens behind the scenes:**
- LiteLLM automatically handles 429 errors
- Waits for Retry-After period before retrying
- Retries up to 3 times (configurable)
- Only returns error if all retries fail

**Related:** [Troubleshooting - Rate Limits and Retry Policies](troubleshooting.md#rate-limits-and-retry-policies)

## Environment Variables Reference

This section provides a complete reference of all environment variables used in AI Gateway. Variables are stored in the `.env` file, which is created during setup.

### Quick Reference

| Category | Variables | Required |
|----------|-----------|----------|
| **Core Security** | `LITELLM_MASTER_KEY`, `VIRTUAL_KEY` | ✅ Yes |
| **PostgreSQL** | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT` | ✅ Yes |
| **UI Credentials** | `UI_USERNAME`, `UI_PASSWORD` | ⚠️ Optional |
| **Ports** | `NGINX_HTTP_PORT`, `LITELLM_EXTERNAL_PORT`, `WEBUI_EXTERNAL_PORT` | ⚠️ Optional |
| **Budget** | `BUDGET_PROFILE` | ⚠️ Optional |
| **Web Search** | `WEB_SEARCH_ENGINE`, `TAVILY_API_KEY`, etc. | ⚠️ Optional |
| **API Keys** | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc. | ⚠️ Optional |
| **Docker Images** | `LITELLM_IMAGE_REPO`, `LITELLM_IMAGE_TAG` | ⚠️ Optional |

### Core Security Variables

#### `LITELLM_MASTER_KEY`

**Required:** ✅ Yes  
**Type:** String  
**Format:** Must start with `sk-`  
**Default:** Auto-generated during setup  
**Description:** Master key for LiteLLM API authentication. Used for admin operations and Virtual Key creation.  
**Security:** ⚠️ **Never expose this key in client applications.** Use Virtual Keys instead.  
**Validation:** 
- Must start with `sk-`
- Minimum length: 35 characters (including `sk-` prefix)
- Generated using: `openssl rand -base64 32` (prefixed with `sk-`)

**Example:**
```bash
LITELLM_MASTER_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
```

**Related:** See [Virtual Key Security](configuration/virtual-key.md#security) for details.

#### `VIRTUAL_KEY`

**Required:** ✅ Yes (after first run)  
**Type:** String  
**Format:** Any string (typically starts with `sk-`)  
**Default:** Empty (created via `virtual-key.sh` or `virtual-key.bat`)  
**Description:** Virtual Key for Open WebUI to authenticate with LiteLLM API. Created via LiteLLM Admin UI or virtual-key script.  
**Security:** ✅ Safe to use in client applications (unlike Master Key)  
**Validation:**
- Can be any string
- Recommended: Use format similar to Master Key (`sk-...`)
- Created via: `./virtual-key.sh` (Linux/macOS) or `virtual-key.bat` (Windows)

**Example:**
```bash
VIRTUAL_KEY=sk-virtual-key-1234567890abcdef
```

**Related:** See [Virtual Key Guide](configuration/virtual-key.md) for creation instructions.

### PostgreSQL Variables

#### `POSTGRES_USER`

**Required:** ✅ Yes  
**Type:** String  
**Default:** `litellm`  
**Description:** PostgreSQL database username.  
**Validation:**
- Must be a valid PostgreSQL identifier
- Cannot be empty
- Recommended: Use lowercase alphanumeric characters

**Example:**
```bash
POSTGRES_USER=litellm
```

#### `POSTGRES_PASSWORD`

**Required:** ✅ Yes  
**Type:** String  
**Default:** Auto-generated during setup (32 characters)  
**Description:** PostgreSQL database password.  
**Validation:**
- Minimum length: 8 characters
- Recommended: 32 characters (auto-generated)
- Generated using: `openssl rand -base64 32` (sanitized)

**Example:**
```bash
POSTGRES_PASSWORD=your-secure-password-here-min-8-chars
```

**Security:** ⚠️ Keep this password secure. It's used for database access.

#### `POSTGRES_DB`

**Required:** ✅ Yes  
**Type:** String  
**Default:** `litellm`  
**Description:** PostgreSQL database name.  
**Validation:**
- Must be a valid PostgreSQL identifier
- Cannot be empty
- Recommended: Use lowercase alphanumeric characters

**Example:**
```bash
POSTGRES_DB=litellm
```

#### `POSTGRES_PORT`

**Required:** ✅ Yes  
**Type:** Integer  
**Default:** `5432`  
**Description:** PostgreSQL internal port (used within Docker network).  
**Validation:**
- Range: 1024-65535
- Must be an integer
- **Note:** This is the internal port. PostgreSQL is never exposed externally.

**Example:**
```bash
POSTGRES_PORT=5432
```

### UI Credentials

#### `UI_USERNAME`

**Required:** ⚠️ Optional  
**Type:** String  
**Default:** `admin`  
**Description:** Username for LiteLLM Admin UI (cost tracking dashboard).  
**Validation:**
- Cannot be empty if `UI_PASSWORD` is set
- Recommended: Use a strong username (not `admin` in production)

**Example:**
```bash
UI_USERNAME=admin
```

**Related:** Access at `http://localhost:PORT/ui` (where PORT is `LITELLM_EXTERNAL_PORT` or Nginx port).

#### `UI_PASSWORD`

**Required:** ⚠️ Optional (required if `UI_USERNAME` is set)  
**Type:** String  
**Default:** Auto-generated during setup (16 characters)  
**Description:** Password for LiteLLM Admin UI.  
**Validation:**
- Minimum length: 8 characters
- Recommended: 16+ characters
- Generated using: `openssl rand -base64 16` (sanitized)

**Example:**
```bash
UI_PASSWORD=your-ui-password-here-min-8-chars
```

**Security:** ⚠️ Change default password in production.

### Port Configuration Variables

#### `NGINX_HTTP_PORT`

**Required:** ⚠️ Optional (required if Nginx is enabled)  
**Type:** Integer  
**Default:** Random high port (49152-65535) if not specified  
**Description:** External port for Nginx reverse proxy.  
**Validation:**
- Range: 1024-65535
- Must be an integer
- Recommended: Use random high ports (49152-65535) for security

**Example:**
```bash
NGINX_HTTP_PORT=63345
```

**Related:** See [Port Configuration](#port-configuration) for details.

#### `NGINX_PORT`

**Required:** ⚠️ Optional (legacy, use `NGINX_HTTP_PORT`)  
**Type:** Integer  
**Default:** Empty  
**Description:** Legacy variable for Nginx port. Use `NGINX_HTTP_PORT` instead.  
**Note:** Both variables may be present for backward compatibility.

#### `LITELLM_EXTERNAL_PORT`

**Required:** ⚠️ Optional  
**Type:** Integer  
**Default:** `4000` (if Nginx disabled) or separate port (if Nginx enabled)  
**Description:** External port for LiteLLM UI access (for admin configuration).  
**Validation:**
- Range: 1024-65535
- Must be an integer
- **Note:** With Nginx, LiteLLM API is accessible via Nginx at `/api/litellm/v1/*`, but UI needs separate port.

**Example:**
```bash
LITELLM_EXTERNAL_PORT=4000
```

#### `WEBUI_EXTERNAL_PORT`

**Required:** ⚠️ Optional (only if Nginx is disabled)  
**Type:** Integer  
**Default:** `3000` (if Nginx disabled)  
**Description:** External port for Open WebUI (only used when Nginx is disabled).  
**Validation:**
- Range: 1024-65535
- Must be an integer
- **Note:** With Nginx enabled, Open WebUI is accessible via Nginx at root `/`.

**Example:**
```bash
WEBUI_EXTERNAL_PORT=3000
```

#### `USE_NGINX`

**Required:** ⚠️ Optional  
**Type:** String (`yes` or `no`)  
**Default:** `yes` (Nginx enabled by default)  
**Description:** Enable or disable Nginx reverse proxy.  
**Validation:**
- Values: `yes`, `true`, `1`, `y` (enabled) or `no`, `false`, `0`, `n` (disabled)
- Case-insensitive

**Example:**
```bash
USE_NGINX=yes
```

### Budget Profile

#### `BUDGET_PROFILE`

**Required:** ⚠️ Optional  
**Type:** String  
**Default:** `test`  
**Description:** Budget profile for cost tracking and limits.  
**Validation:**
- Values: `test`, `prod`, `unlimited`
- Case-sensitive

**Profiles:**
- `test`: $15/month budget limit
- `prod`: $200/month budget limit
- `unlimited`: $1000/month budget limit (effectively unlimited)

**Example:**
```bash
BUDGET_PROFILE=prod
```

**Related:** See [Budget Profiles](#budget-profiles) for details.

**Usage:**
- Set in `.env` file
- Or override when starting: `./start.sh prod`

### Web Search Variables

#### `WEB_SEARCH_ENGINE`

**Required:** ⚠️ Optional  
**Type:** String  
**Default:** `tavily`  
**Description:** Web search engine to use for AI model web search functionality.  
**Validation:**
- Values: `tavily`, `google_pse`, `serper`, `brave`, `kagi`
- Case-sensitive

**Example:**
```bash
WEB_SEARCH_ENGINE=tavily
```

**Related:** See [Web Search Configuration](#web-search-configuration) for details.

#### `TAVILY_API_KEY`

**Required:** ⚠️ Optional (required if `WEB_SEARCH_ENGINE=tavily`)  
**Type:** String  
**Default:** Empty  
**Description:** API key for Tavily search engine.  
**Validation:**
- Cannot be empty if `WEB_SEARCH_ENGINE=tavily`
- Get key at: https://tavily.com/
- Free tier: 1000 searches/month

**Example:**
```bash
TAVILY_API_KEY=your-tavily-api-key-here
```

#### `GOOGLE_PSE_API_KEY`

**Required:** ⚠️ Optional (required if `WEB_SEARCH_ENGINE=google_pse`)  
**Type:** String  
**Default:** Empty  
**Description:** API key for Google Programmable Search Engine.  
**Validation:**
- Cannot be empty if `WEB_SEARCH_ENGINE=google_pse`
- Setup: https://programmablesearchengine.google.com/

**Example:**
```bash
GOOGLE_PSE_API_KEY=your-google-pse-api-key-here
```

#### `SERPER_API_KEY`

**Required:** ⚠️ Optional (required if `WEB_SEARCH_ENGINE=serper`)  
**Type:** String  
**Default:** Empty  
**Description:** API key for Serper search engine.  
**Validation:**
- Cannot be empty if `WEB_SEARCH_ENGINE=serper`
- Get key at: https://serper.dev/

**Example:**
```bash
SERPER_API_KEY=your-serper-api-key-here
```

#### `BRAVE_API_KEY`

**Required:** ⚠️ Optional (required if `WEB_SEARCH_ENGINE=brave`)  
**Type:** String  
**Default:** Empty  
**Description:** API key for Brave search engine.  
**Validation:**
- Cannot be empty if `WEB_SEARCH_ENGINE=brave`

**Example:**
```bash
BRAVE_API_KEY=your-brave-api-key-here
```

#### `KAGI_API_KEY`

**Required:** ⚠️ Optional (required if `WEB_SEARCH_ENGINE=kagi`)  
**Type:** String  
**Default:** Empty  
**Description:** API key for Kagi search engine.  
**Validation:**
- Cannot be empty if `WEB_SEARCH_ENGINE=kagi`
- **Note:** Kagi is paid-only (no free tier)

**Example:**
```bash
KAGI_API_KEY=your-kagi-api-key-here
```

#### `WEB_SEARCH_CONCURRENT_REQUESTS`

**Required:** ⚠️ Optional  
**Type:** Integer  
**Default:** Auto-set based on resource profile (1-3)  
**Description:** Number of concurrent web search requests.  
**Validation:**
- Range: 1-10 (recommended: 1-3)
- Must be an integer
- Higher values = more CPU/memory usage

**Profile Defaults:**
- Small/Medium VPS: `1`
- Large VPS: `2`
- Desktop: `3`

**Example:**
```bash
WEB_SEARCH_CONCURRENT_REQUESTS=2
```

#### `WEB_SEARCH_RESULT_COUNT`

**Required:** ⚠️ Optional  
**Type:** Integer  
**Default:** Auto-set based on resource profile (1-4)  
**Description:** Number of search results to fetch per query.  
**Validation:**
- Range: 1-10 (recommended: 1-4)
- Must be an integer
- Higher values = better context but more API usage

**Profile Defaults:**
- Small/Medium VPS: `1`
- Large VPS: `3`
- Desktop: `4`

**Example:**
```bash
WEB_SEARCH_RESULT_COUNT=3
```

#### `BYPASS_WEB_SEARCH_WEB_LOADER`

**Required:** ⚠️ Optional  
**Type:** String (`true` or `false`)  
**Default:** `true`  
**Description:** Bypass web loader (Playwright). Set to `true` because web loader is not bundled.  
**Validation:**
- Values: `true`, `false`
- **Note:** Only set to `false` if you run your own scraping engine elsewhere

**Example:**
```bash
BYPASS_WEB_SEARCH_WEB_LOADER=true
```

#### `UPDATE_WEB_SEARCH_SETTINGS`

**Required:** ⚠️ Optional  
**Type:** String (`yes` or `no`)  
**Default:** `no`  
**Description:** Flag to update OpenWebUI web search settings from environment variables on next container start.  
**Validation:**
- Values: `yes`, `no`
- Automatically set to `yes` when profile is changed during setup
- Automatically cleared after successful update

**Example:**
```bash
UPDATE_WEB_SEARCH_SETTINGS=yes
```

### Open WebUI Variables

#### `WEBUI_SECRET_KEY`

**Required:** ⚠️ Optional  
**Type:** String  
**Default:** Auto-generated during setup (32 characters)  
**Description:** Secret key for Open WebUI security.  
**Validation:**
- Minimum length: 16 characters
- Recommended: 32 characters (auto-generated)
- Generated using: `openssl rand -base64 32` (sanitized)

**Example:**
```bash
WEBUI_SECRET_KEY=your-webui-secret-key-here-min-16-chars
```

**Security:** ⚠️ Keep this key secure. Used for session encryption.

### API Keys for LLM Providers

**Required:** ⚠️ Optional (not required for setup/start)  
**Description:** API keys for various LLM providers. Can be added in `.env` or via LiteLLM Admin UI.  
**Note:** API keys are **NOT required** for initial setup. You can add them later through LiteLLM Admin UI at `http://localhost:PORT/ui`.

**Supported Providers:** 100+ providers supported by LiteLLM. See: https://docs.litellm.ai/docs/providers

**Common API Keys:**

| Variable | Provider | Get Key |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | Anthropic Claude | https://console.anthropic.com/ |
| `OPENAI_API_KEY` | OpenAI GPT | https://platform.openai.com/api-keys |
| `GEMINI_API_KEY` | Google Gemini | https://makersuite.google.com/app/apikey |
| `GOOGLE_API_KEY` | Google AI (alternative) | https://makersuite.google.com/app/apikey |
| `GROQ_API_KEY` | Groq | https://console.groq.com/keys |
| `DEEPSEEK_API_KEY` | Deepseek | https://deepseek.com/ |
| `MISTRAL_API_KEY` | Mistral AI | https://console.mistral.ai/ |
| `TOGETHER_API_KEY` | Together AI | https://together.ai/ |
| `PERPLEXITY_API_KEY` | Perplexity AI | https://www.perplexity.ai |
| `XAI_API_KEY` | xAI (Grok) | https://docs.x.ai/docs |
| `COHERE_API_KEY` | Cohere | https://cohere.com/ |
| `FIREWORKS_API_KEY` | Fireworks AI | https://fireworks.ai/ |
| `OPENROUTER_API_KEY` | OpenRouter | https://openrouter.ai/ |
| `AZURE_API_KEY` | Azure OpenAI | Azure Portal |
| `AZURE_API_BASE` | Azure OpenAI | Azure Portal |
| `AZURE_API_VERSION` | Azure OpenAI | Azure Portal |

**Example:**
```bash
# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# OpenAI GPT
OPENAI_API_KEY=your-openai-api-key-here

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key-here
```

**Related:** See [Getting Started - Step 3](getting-started.md#step-3-access-and-configure) for adding providers via Admin UI.

### Docker Image Configuration

#### `LITELLM_IMAGE_REPO`

**Required:** ⚠️ Optional  
**Type:** String  
**Default:** `ghcr.io/berriai/litellm`  
**Description:** Docker image repository for LiteLLM.  
**Validation:**
- Must be a valid Docker image repository
- Recommended: Use official repository `ghcr.io/berriai/litellm`

**Example:**
```bash
LITELLM_IMAGE_REPO=ghcr.io/berriai/litellm
```

**Related:** See [env.example](../env.example) for details.

#### `LITELLM_IMAGE_TAG`

**Required:** ⚠️ Optional  
**Type:** String  
**Default:** `main-stable`  
**Description:** Docker image tag for LiteLLM.  
**Validation:**
- Must be a valid Docker image tag
- Recommended: Use `main-stable` (stable version)
- ⚠️ **Warning:** `main-latest` may have Prisma migration loop bug

**Example:**
```bash
LITELLM_IMAGE_TAG=main-stable
```

**Available Tags:**
- Official (GitHub): https://github.com/orgs/BerriAI/packages/container/litellm
- Docker Hub: https://hub.docker.com/r/litellm/litellm/tags

### Internal Variables

These variables are used internally and typically don't need to be modified:

#### Variables Set Automatically in Docker Compose

The following variables are set automatically in `docker-compose.yml` or `docker-compose.override.yml` and **do not need to be set in `.env`**:

| Variable | Set In | Default Value | Description |
|----------|--------|---------------|-------------|
| `DATABASE_URL` | `docker-compose.yml` | Auto-generated from PostgreSQL vars | PostgreSQL connection string |
| `STORE_MODEL_IN_DB` | `docker-compose.yml` | `True` | Enable model storage in database |
| `LITELLM_NUM_RETRIES` | `docker-compose.yml` | `3` | Number of retries for failed requests |
| `LITELLM_TIMEOUT` | `docker-compose.yml` | `600` | Request timeout in seconds (10 minutes) |
| `LITELLM_LOG_LEVEL` | `docker-compose.override.yml` | `DEBUG` | Logging level for LiteLLM |
| `SET_VERBOSE` | `docker-compose.override.yml` | `True` | Enable verbose logging |
| `PYTHONPATH` | `docker-compose.override.yml` | `/app:/app/litellm_callbacks` | Python path for custom callbacks |

**Note:** These variables are managed automatically and should not be modified unless you understand the implications. They are included here for reference only.

#### `FIRST_RUN`

**Required:** ⚠️ Optional  
**Type:** String (`yes` or `no`)  
**Default:** `yes` (on first setup)  
**Description:** Flag indicating first run. Set to `no` after Virtual Key setup.  
**Note:** Used internally to show setup instructions. Don't modify manually.

#### `LITELLM_INTERNAL_PORT`

**Required:** ⚠️ Optional  
**Type:** Integer  
**Default:** `4000`  
**Description:** Internal port for LiteLLM (used within Docker network).  
**Note:** This is the internal port. External access is via `LITELLM_EXTERNAL_PORT` or Nginx.

#### `WEBUI_INTERNAL_PORT`

**Required:** ⚠️ Optional  
**Type:** Integer  
**Default:** `8080`  
**Description:** Internal port for Open WebUI (used within Docker network).  
**Note:** This is the internal port. External access is via `WEBUI_EXTERNAL_PORT` or Nginx.

### Configuration Examples

#### Minimal Configuration (Required Variables Only)

```bash
# Core Security
LITELLM_MASTER_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
VIRTUAL_KEY=sk-virtual-key-1234567890abcdef

# PostgreSQL
POSTGRES_USER=litellm
POSTGRES_PASSWORD=your-secure-password-here-min-8-chars
POSTGRES_DB=litellm
POSTGRES_PORT=5432
```

#### Production Configuration (Recommended)

```bash
# Core Security
LITELLM_MASTER_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
VIRTUAL_KEY=sk-virtual-key-1234567890abcdef

# PostgreSQL
POSTGRES_USER=litellm
POSTGRES_PASSWORD=your-secure-password-here-min-8-chars
POSTGRES_DB=litellm
POSTGRES_PORT=5432

# UI Credentials
UI_USERNAME=admin
UI_PASSWORD=your-ui-password-here-min-8-chars

# Ports (with Nginx)
USE_NGINX=yes
NGINX_HTTP_PORT=63345
LITELLM_EXTERNAL_PORT=4000

# Budget
BUDGET_PROFILE=prod

# Web Search
WEB_SEARCH_ENGINE=tavily
TAVILY_API_KEY=your-tavily-api-key-here
WEB_SEARCH_CONCURRENT_REQUESTS=2
WEB_SEARCH_RESULT_COUNT=3

# API Keys
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Open WebUI
WEBUI_SECRET_KEY=your-webui-secret-key-here-min-16-chars
```

#### Development Configuration (Local)

```bash
# Core Security
LITELLM_MASTER_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
VIRTUAL_KEY=sk-virtual-key-1234567890abcdef

# PostgreSQL
POSTGRES_USER=litellm
POSTGRES_PASSWORD=dev-password-123
POSTGRES_DB=litellm
POSTGRES_PORT=5432

# Budget
BUDGET_PROFILE=test

# Ports (without Nginx for easier debugging)
USE_NGINX=no
LITELLM_EXTERNAL_PORT=4000
WEBUI_EXTERNAL_PORT=3000
```

### Validation Summary

| Variable | Required | Type | Min Length | Max Length | Format/Values |
|----------|----------|------|------------|------------|---------------|
| `LITELLM_MASTER_KEY` | ✅ | String | 35 | - | Must start with `sk-` |
| `VIRTUAL_KEY` | ✅* | String | 1 | - | Any string |
| `POSTGRES_USER` | ✅ | String | 1 | - | Valid PostgreSQL identifier |
| `POSTGRES_PASSWORD` | ✅ | String | 8 | - | Any string |
| `POSTGRES_DB` | ✅ | String | 1 | - | Valid PostgreSQL identifier |
| `POSTGRES_PORT` | ✅ | Integer | - | - | 1024-65535 |
| `UI_USERNAME` | ⚠️ | String | 1 | - | Any string |
| `UI_PASSWORD` | ⚠️ | String | 8 | - | Any string |
| `NGINX_HTTP_PORT` | ⚠️ | Integer | - | - | 1024-65535 |
| `LITELLM_EXTERNAL_PORT` | ⚠️ | Integer | - | - | 1024-65535 |
| `WEBUI_EXTERNAL_PORT` | ⚠️ | Integer | - | - | 1024-65535 |
| `USE_NGINX` | ⚠️ | String | - | - | `yes`/`no` |
| `BUDGET_PROFILE` | ⚠️ | String | - | - | `test`/`prod`/`unlimited` |
| `WEB_SEARCH_ENGINE` | ⚠️ | String | - | - | `tavily`/`google_pse`/`serper`/`brave`/`kagi` |
| `WEBUI_SECRET_KEY` | ⚠️ | String | 16 | - | Any string |

*Required after first run

### Environment File Location

The `.env` file is located in the project root directory (same directory as `docker-compose.yml`).

**File Permissions:**
- Default: `600` (owner read/write only)
- Set automatically during setup
- **Security:** Never commit `.env` to version control

**Viewing Variables:**
```bash
# View all variables
cat .env

# View specific variable
grep VARIABLE_NAME .env

# View all port-related variables
grep -i port .env
```

**Editing Variables:**
```bash
# Edit with your preferred editor
nano .env
# or
vim .env
```

**After Editing:**
- Restart containers to apply changes: `./stop.sh && ./start.sh`
- Or restart specific service: `docker compose restart SERVICE_NAME`

### Related Documentation

- [Getting Started Guide](getting-started.md) - Initial setup and configuration
- [Virtual Key Guide](configuration/virtual-key.md) - Virtual Key creation and security
- [Troubleshooting Guide](troubleshooting.md) - Common configuration issues
- [Security Guide](security.md) - Security best practices
- [env.example](../env.example) - Example environment file with all variables

