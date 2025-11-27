# Frequently Asked Questions (FAQ)

<!--
Tags for AI agents:
- faq
- frequently-asked-questions
- common-questions
- troubleshooting
- help
- quick-answers
-->

This FAQ answers the most common questions about AI Gateway. For detailed information, see the linked documentation.

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Performance](#performance)
- [API and Integration](#api-and-integration)
- [Models and Providers](#models-and-providers)

## Getting Started

### Q: How long does setup take?

**A:** Setup typically takes about 5 minutes. The setup script guides you through:
- Resource profile selection
- Budget profile selection
- Port configuration
- Environment file generation

**Related:** [Getting Started Guide](getting-started.md#step-1-run-setup-script)

### Q: What are the minimum system requirements?

**A:** Minimum requirements:
- **RAM:** 3GB (4GB recommended)
- **CPU:** 2 cores (4 cores recommended)
- **Disk:** 10GB free space
- **Docker:** 20.10 or higher
- **Python:** 3.8 or higher

**Related:** [System Requirements](system-requirements.md)

### Q: Can I run this on a 2GB VPS?

**A:** ⚠️ **Possible but tight.** Small VPS (2GB) actually uses ~2.3-2.5GB, exceeding 2GB by 15-25%. 

**Recommendations:**
- **Best option:** Upgrade to 4GB (Medium VPS) ⭐
- **Alternative:** Use lightweight Linux (Alpine, Debian minimal) to reduce overhead to ~2.0GB
- **Last resort:** Reduce to 1 worker (but performance will be limited)

**Related:** [System Requirements - Small VPS](system-requirements.md#small-vps-2gb-ram-2-cpu-cores)

### Q: Do I need API keys to start the system?

**A:** No! API keys are **NOT required** for setup/start. You can:
1. Run setup and start without any API keys
2. Add API keys later through LiteLLM Admin UI at `http://localhost:PORT/ui`
3. Configure providers and models after startup

**Related:** [Getting Started - Step 3](getting-started.md#step-3-access-and-configure)

### Q: What files are created during setup?

**A:** Setup creates three files:
- **`.env`** - Environment variables (sensitive, permissions: 600)
- **`config.yaml`** - LiteLLM configuration (permissions: 644)
- **`docker-compose.override.yml`** - Docker Compose overrides (permissions: 600)

All files are automatically added to `.gitignore`.

**Related:** [Getting Started - Generated Files](getting-started.md#generated-files)

## Configuration

### Q: What is a Virtual Key and why do I need it?

**A:** Virtual Key is a secure API key for Open WebUI to authenticate with LiteLLM API. It's different from Master Key:
- **Master Key:** ⚠️ Never use in client applications (admin operations only)
- **Virtual Key:** ✅ Safe to use in client applications

**Why:** After first run, Virtual Key becomes mandatory for security. Master Key should not be used directly.

**Related:** [Virtual Key Guide](configuration/virtual-key.md)

### Q: How do I create a Virtual Key?

**A:** Run the virtual-key script:
```bash
# Linux/macOS
./virtual-key.sh

# Windows
virtual-key.bat
```

The Virtual Key will be saved to `.env` automatically.

**Related:** [Virtual Key Guide - Creation](configuration/virtual-key.md#creating-a-virtual-key)

### Q: What ports are used by default?

**A:** Default ports:
- **Nginx:** Random high port (49152-65535) or configured port
- **LiteLLM API:** 4000 (or via Nginx at `/api/litellm/v1/*`)
- **LiteLLM UI:** 4000 (or separate port if configured)
- **Open WebUI:** Via Nginx at `/` (or 3000 if Nginx disabled)
- **PostgreSQL:** 5432 (internal only, never exposed)

**Related:** [Port Configuration](configuration.md#port-configuration)

### Q: Can I change ports after setup?

**A:** Yes, but you need to:
1. Edit `.env` file with new ports
2. Update `docker-compose.override.yml` if needed
3. Restart containers: `./stop.sh && ./start.sh`

**Better approach:** Re-run setup: `./ai-gateway setup` (will preserve existing configuration)

**Related:** [Port Configuration](configuration.md#port-configuration)

### Q: Do I need to set all environment variables in .env?

**A:** No. Some variables are set automatically in `docker-compose.yml` or `docker-compose.override.yml` and don't need to be in `.env`:

- `DATABASE_URL` - Auto-generated from PostgreSQL variables
- `STORE_MODEL_IN_DB` - Set to `True` automatically
- `LITELLM_NUM_RETRIES` - Set to `3` automatically
- `LITELLM_TIMEOUT` - Set to `600` automatically
- `LITELLM_LOG_LEVEL` - Set to `DEBUG` in override file
- `SET_VERBOSE` - Set to `True` in override file
- `PYTHONPATH` - Set automatically for callbacks

**Required in `.env`:**
- `LITELLM_MASTER_KEY` - Must start with `sk-`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- `VIRTUAL_KEY` - Created after first setup

**Related:** [Configuration Guide - Variables Set Automatically](configuration.md#variables-set-automatically-in-docker-compose)

### Q: What is the difference between resource profiles?

**A:** Resource profiles optimize system for different hardware:

| Profile | RAM | CPU | Workers | Users |
|---------|-----|-----|---------|-------|
| **Desktop** | Unlimited | Unlimited | 4 | Local dev |
| **Small VPS** | 2GB | 2 CPU | 1 | 1-2 users ⚠️ |
| **Medium VPS** | 4GB | 4 CPU | 2 | 3-5 users ⭐ |
| **Large VPS** | 8GB+ | 8 CPU | 6 | 10+ users |

**Related:** [Resource Profiles](configuration.md#resource-profiles)

### Q: What is a budget profile?

**A:** Budget profile sets monthly spending limits:
- **test:** $15/month
- **prod:** $200/month
- **unlimited:** $1000/month (effectively unlimited)

**Related:** [Budget Profiles](configuration.md#budget-profiles)

### Q: How do I change the budget profile?

**A:** Two ways:
1. **In `.env`:** Set `BUDGET_PROFILE=prod` (or `test`/`unlimited`)
2. **When starting:** `./start.sh prod` (or `test`/`unlimited`)

**Related:** [Budget Profiles](configuration.md#budget-profiles)

## Troubleshooting

### Q: Containers won't start. What should I do?

**A:** Check these common issues:

1. **Virtual Key missing (after first run):**
   ```bash
   ./virtual-key.sh  # Create Virtual Key
   ./stop.sh && ./start.sh  # Restart
   ```

2. **Port conflicts:**
   ```bash
   # Find what's using the port
   sudo lsof -i :PORT
   # Or use different ports
   ```

3. **Docker not running:**
   ```bash
   docker ps  # Check Docker is running
   ```

4. **View logs:**
   ```bash
   docker compose logs  # All services
   docker compose logs litellm  # Specific service
   ```

**Related:** [Troubleshooting Guide](troubleshooting.md#containers-wont-start)

### Q: I see "Virtual Key not found" error. What does this mean?

**A:** This means Virtual Key is missing from `.env` file. This happens after first run when Virtual Key becomes mandatory.

**Solution:**
1. Create Virtual Key: `./virtual-key.sh` (Linux/macOS) or `virtual-key.bat` (Windows)
2. Restart containers: `./stop.sh && ./start.sh`

**Note:** On first run, system allows Master Key as fallback. After first run, Virtual Key is required.

**Related:** [Troubleshooting - Virtual Key](troubleshooting.md#virtual-key-not-found-or-virtual-key-is-required)

### Q: I see "master key invalid" error. What's wrong?

**A:** Master Key must start with `sk-`. Check:

```bash
grep LITELLM_MASTER_KEY .env
```

**Solution:**
1. Master Key must start with `sk-` (e.g., `sk-1234567890abcdef...`)
2. If incorrect, re-run setup: `./setup.sh`
3. Restart containers: `./stop.sh && ./start.sh`

**Related:** [Troubleshooting - Master Key](troubleshooting.md#master-key-invalid-error)

### Q: Port is already in use. How do I fix this?

**A:** Find what's using the port and either stop it or use a different port:

```bash
# Linux/macOS
sudo lsof -i :PORT
# Or
sudo netstat -tulpn | grep :PORT

# Windows
netstat -ano | findstr :PORT
```

**Solutions:**
- Use random high ports (49152-65535) for better security
- Stop conflicting service
- Re-run setup and choose different ports

**Related:** [Troubleshooting - Port Conflicts](troubleshooting.md#port-conflicts)

### Q: Models don't appear in Open WebUI. Why?

**A:** Check these:

1. **Models configured in LiteLLM Admin UI?**
   - Access: `http://localhost:PORT/ui`
   - Go to Models section
   - Verify models are saved

2. **Providers have valid API keys?**
   - Check API keys in LiteLLM Admin UI
   - Verify keys are correct and active

3. **Virtual Key set?**
   ```bash
   grep VIRTUAL_KEY .env
   ```

4. **Try refreshing Open WebUI page**

5. **Last resort:** `docker compose restart litellm`

**Related:** [Troubleshooting - Models](troubleshooting.md#models-dont-appear-in-open-webui)

### Q: I'm getting "Out of Memory" errors. What should I do?

**A:** Check current memory usage:

```bash
# Check container memory usage
docker stats --no-stream

# Check system memory
free -h
```

**Solutions:**
1. **Upgrade to larger VPS** (Medium VPS recommended for 4GB systems)
2. **Reduce workers** (edit `docker-compose.override.yml`, change `--num_workers`)
3. **For Small VPS:** Use lightweight Linux distribution (Alpine, Debian minimal)

**Related:** [Troubleshooting - Memory Issues](troubleshooting.md#memory-issues--out-of-memory-oom-errors)

### Q: PostgreSQL won't connect. How do I fix it?

**A:** If password was changed, remove the volume:

```bash
docker compose down -v
docker compose up -d
```

⚠️ **Warning:** This will delete all PostgreSQL data!

**Related:** [Troubleshooting - PostgreSQL](troubleshooting.md#postgresql-wont-connect)

## Security

### Q: Is it safe to use Master Key in client applications?

**A:** ❌ **No!** Never use Master Key in client applications. Use Virtual Key instead.

**Why:**
- Master Key has full admin access
- Virtual Key can be restricted to specific models/endpoints
- Virtual Key is safer for client applications

**Related:** [Virtual Key Security](configuration/virtual-key.md#security)

### Q: How do I secure my installation for production?

**A:** Security recommendations:

1. **Change default passwords:**
   - `UI_USERNAME` and `UI_PASSWORD` in `.env`
   - PostgreSQL password

2. **Use Virtual Keys:**
   - Never use Master Key in client applications
   - Create separate Virtual Keys for different applications

3. **Set up SSL/HTTPS:**
   - Use external Nginx with Let's Encrypt
   - See [Nginx Configuration](nginx/README.md)

4. **Firewall configuration:**
   - Only expose necessary ports
   - Use VPN for remote access

5. **Keep `.env` secure:**
   - Permissions: 600 (owner only)
   - Never commit to version control

**Related:** [Security Guide](security.md)

### Q: Can I access services from other devices on my network?

**A:** Yes! By default, services are accessible from:
- **localhost** (127.0.0.1) - same machine
- **Local network** - other devices on same network

**To access from other devices:**
1. Find your server IP: `ip addr show` (Linux) or `ipconfig` (Windows)
2. Replace `localhost` with server IP: `http://192.168.1.100:PORT`

**Note:** Make sure firewall allows connections on the configured ports.

**Related:** [Network Access](configuration.md#network-access)

## Performance

### Q: How much RAM does the system use?

**A:** Memory usage (measured, idle, Medium VPS profile):
- **litellm:** ~1.177 GiB (with 2 workers)
  - Base: ~300-320MB
  - Per worker: ~460MB
- **open-webui:** ~602MB
- **postgres:** ~48MB (idle)
- **nginx:** ~5-6MB
- **Docker overhead:** ~200MB

**Total:** ~3.3GB for Medium VPS profile

**Related:** [Memory Configuration](configuration.md#memory-configuration)

### Q: How many users can the system handle?

**A:** Depends on resource profile:

| Profile | Users | Description |
|---------|-------|-------------|
| **Small VPS** | 1-2 | Light use, occasional requests |
| **Medium VPS** | 3-5 | Regular use, moderate load ⭐ |
| **Large VPS** | 10+ | Active use, high load |

**Note:** Actual capacity depends on:
- Request frequency
- Model complexity
- Response length
- Concurrent requests

**Related:** [Resource Profiles](configuration.md#resource-profiles)

### Q: Can I reduce memory usage?

**A:** Yes, several options:

1. **Reduce LiteLLM workers:**
   - Edit `docker-compose.override.yml`
   - Change `--num_workers` (e.g., from 2 to 1)
   - Each worker uses ~460MB RAM

2. **Use lightweight Linux:**
   - Alpine Linux, Debian minimal, Ubuntu Server minimal
   - Reduces system overhead from ~1.2GB to ~0.7GB

3. **Upgrade to larger VPS:**
   - More RAM = better performance
   - Medium VPS (4GB) recommended

**Related:** [Memory Configuration](configuration.md#memory-configuration)

## API and Integration

### Q: How do I use the API?

**A:** API is accessible at:
- **With Nginx:** `http://localhost:PORT/api/litellm/v1/*`
- **Without Nginx:** `http://localhost:4000/v1/*`

**Authentication:**
```bash
curl http://localhost:PORT/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY"
```

**Related:** [API for Agents](integrations/api-for-agents.md)

### Q: How do I get OpenAPI specification?

**A:** OpenAPI spec is available at:
- **Inside container:** `http://localhost:4000/openapi.json`
- **External port:** `http://localhost:LITELLM_EXTERNAL_PORT/openapi.json` (requires Master Key)

**Get spec:**
```bash
# From host
curl http://localhost:PORT/openapi.json \
  -H "Authorization: Bearer YOUR_MASTER_KEY" \
  -o openapi.json

# From inside container
docker exec litellm-proxy wget -qO /tmp/openapi.json http://localhost:4000/openapi.json
docker cp litellm-proxy:/tmp/openapi.json ./openapi.json
```

**Related:** [API for Agents - OpenAPI Spec](integrations/api-for-agents.md#getting-openapi-specification)

### Q: Can I integrate with Continue.dev?

**A:** Yes! Continue.dev integration is supported with automatic model discovery.

**Setup:**
1. Install Continue.dev extension in VS Code
2. Configure `config.json` (see [Continue.dev Integration](integrations/continue-dev.md))
3. Models are automatically discovered from LiteLLM API

**Related:** [Continue.dev Integration](integrations/continue-dev.md)

### Q: Can I use this with GitHub Copilot?

**A:** ⚠️ **Experimental.** GitHub Copilot integration is experimental. **Recommended:** Use Continue.dev instead, which has better support and automatic model discovery.

**Related:** [GitHub Copilot Integration](integrations/github-copilot.md)

## Models and Providers

### Q: Which providers are supported?

**A:** LiteLLM supports 100+ providers. Common providers:
- Anthropic (Claude)
- OpenAI (GPT)
- Google AI Studio (Gemini)
- Mistral AI
- Groq
- Deepseek
- Together AI
- Perplexity AI
- And 90+ more...

**Related:** [LiteLLM Providers](https://docs.litellm.ai/docs/providers)

### Q: How do I add a new provider?

**A:** Steps:

1. **Get API key** from provider
2. **Add to `.env`** or **LiteLLM Admin UI:**
   - Via `.env`: Add `PROVIDER_API_KEY=your-key-here`
   - Via UI: Go to `http://localhost:PORT/ui` → Providers → Add Provider
3. **Add models** in LiteLLM Admin UI → Models → Add Model
4. **Models appear automatically** in Open WebUI (no restart needed)

**Related:** [Getting Started - Step 3](getting-started.md#step-3-access-and-configure)

### Q: How do I find the correct model ID?

**A:** Model IDs may differ from provider's official names. **Always verify:**

1. **Via API:**
   ```bash
   curl http://localhost:PORT/api/litellm/v1/models \
     -H "Authorization: Bearer YOUR_KEY"
   ```

2. **Via LiteLLM Admin UI:**
   - Go to Models section
   - See configured models

3. **Via Provider Documentation:**
   - Check [LiteLLM Providers Docs](https://docs.litellm.ai/docs/providers)
   - Check provider's official documentation

**Related:** [Getting Started - Model IDs](getting-started.md#step-33-add-models)

### Q: Models are not working. What should I check?

**A:** Check these:

1. **API key is valid:**
   - Verify in LiteLLM Admin UI
   - Check API key is active and has quota

2. **Model ID is correct:**
   - Verify model ID matches provider's format
   - Check [LiteLLM Provider Docs](https://docs.litellm.ai/docs/providers)

3. **Provider is configured:**
   - Check provider exists in LiteLLM Admin UI
   - Verify API key is set

4. **Check logs:**
   ```bash
   docker compose logs litellm | grep -i error
   ```

**Related:** [Troubleshooting - Models](troubleshooting.md#models-dont-appear-in-open-webui)

### Q: Can I use multiple providers at the same time?

**A:** Yes! You can configure multiple providers and use different models from different providers simultaneously.

**Example:**
- Claude (Anthropic) for complex tasks
- GPT-4 (OpenAI) for general tasks
- Gemini (Google) for specific use cases

All models appear in Open WebUI and can be selected per conversation.

**Related:** [Getting Started - Step 3](getting-started.md#step-3-access-and-configure)

## Still Have Questions?

- **Documentation:** See [Documentation Index](README.md)
- **Troubleshooting:** See [Troubleshooting Guide](troubleshooting.md)
- **Getting Started:** See [Getting Started Guide](getting-started.md)
- **Configuration:** See [Configuration Guide](configuration.md)
- **Issues:** Check GitHub issues or create a new one

---

**Last Updated:** 2025-11-26  
**For AI Agents:** This FAQ contains tags for semantic search. Use tags: `faq`, `frequently-asked-questions`, `common-questions`, `troubleshooting`, `help`, `quick-answers`

