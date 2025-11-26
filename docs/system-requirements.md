# System Requirements

## Minimum Requirements

- **Python**: 3.8 or higher
- **Docker**: 20.10 or higher (Docker Compose v2 recommended)
- **RAM**: 3GB minimum (4GB recommended) ⚠️ **Note**: Small VPS (2GB) profile uses ~2.3-2.5GB on typical Linux, or ~2.0GB with lightweight distro - see [Resource Profiles](#resource-profiles) below
- **CPU**: 2 cores minimum (4 cores recommended)
- **Disk**: 10GB minimum (see [Disk Space Requirements](#disk-space-requirements) below for details)
- **OS**: Linux (tested), macOS (experimental, not fully tested), Windows with WSL2 (experimental, not fully tested)

## Recommended Requirements

- **RAM**: 4GB+ for better performance
- **CPU**: 4+ cores for better performance
- **Network**: Stable internet connection for API calls to LLM providers

## ⚠️ Proxmox LXC Containers

**Rootless Docker is not reliably supported in unprivileged Proxmox LXC containers** due to kernel-level restrictions on user namespaces. If you're using Proxmox, we recommend:

- **Use a full VM** instead of an LXC container for running AI Gateway
- **Or use a privileged LXC container** (less secure, but may work)

For more details, see the [Installation Guide](installation.md#proxmox-lxc-containers).

## 💡 Tips for Small VPS (2GB) Users

If you're using a Small VPS with 2GB RAM, consider using a **lightweight Linux distribution** to reduce system overhead:

### Recommended Lightweight Distributions

- **Alpine Linux** - Very lightweight (~5MB base), uses musl libc
- **Debian minimal** - Minimal Debian installation without desktop environment
- **Ubuntu Server minimal** - Minimal Ubuntu Server installation

### Memory Savings

- **System overhead reduction**: From ~1.2GB (typical Linux) to ~0.7GB (lightweight distro)
- **Total usage with lightweight distro (with request buffer)**: ~2.0GB (fits in 2GB, tight but feasible)
- **Total usage with typical Linux (with request buffer)**: ~2.3-2.5GB (exceeds 2GB by 15-25%) ⚠️

### Installation Notes

- Lightweight distributions typically have minimal package sets
- Docker installation may require additional packages
- Some distributions may need manual configuration for rootless Docker
- See [Installation Guide](installation.md) for platform-specific instructions

### Important Notes

- ⚠️ Even with a lightweight distro, 2GB is still tight. Medium VPS (4GB) is **strongly recommended** for better performance and safety.
- Monitor memory usage: `docker stats` and `free -h`
- Consider upgrading to Medium VPS (4GB) if you experience OOM (Out of Memory) errors

## Resource Profiles

Each profile sets Docker container resource limits. **Memory usage is based on real measurements (2025-11-24)**. The host system should have:

### Small VPS: 2GB RAM, 2 CPU cores

- ⚠️ **WARNING**: Actual usage is ~2.3-2.5GB on typical Linux distributions (exceeds 2GB by 15-25%)
- Containers (idle): ~1.063 GiB (LiteLLM: 426.5MB with 1 worker, Open WebUI: 603MB, PostgreSQL: 27MB, Nginx: 6MB, Docker: ~200MB)
- Containers (with request buffer): ~1.3 GiB (+200-300MB for active requests)
- System overhead: ~1.2GB (typical Linux) or ~0.7GB (lightweight distro)
- **Total (typical Linux, with buffer)**: ~2.5GB (exceeds 2GB by 25%) ⚠️
- **Total (lightweight distro, with buffer)**: ~2.0GB (fits in 2GB, tight) ⚠️
- **Base usage (typical Linux, idle)**: ~2.3GB (containers + system overhead)
- **Recommendations**:
  - **Option 1**: Use Medium VPS (4GB) for safety ⭐ **Recommended**
  - **Option 2**: Use lightweight Linux distribution (Alpine, Debian minimal, Ubuntu Server minimal) to reduce system overhead, bringing total to ~2.0GB (tight but feasible)

### Medium VPS: 4GB RAM, 4 CPU cores ⭐ **Recommended**

- Containers (idle): ~1.8 GiB (LiteLLM: 1.177 GiB with 2 workers, Open WebUI: 602MB, PostgreSQL: 48MB, Nginx: 6MB, Docker: ~200MB)
- Containers (with request buffer): ~2.1-2.2 GiB (+300-400MB for active requests)
- System overhead: ~1.2GB
- **Total (with buffer)**: ~3.3-3.4GB (safe with ~600-700MB buffer) ✓
- **Base usage (idle)**: ~3.0GB (containers + system overhead)

### Large VPS: 8GB+ RAM, 8 CPU cores

- Containers (idle): ~3.9 GiB (LiteLLM: 3.08GB with 6 workers, Open WebUI: 602MB, PostgreSQL: 48MB, Nginx: 6MB, Docker: ~200MB)
- Containers (with request buffer): ~4.5-4.7 GiB (+600-800MB for high concurrency)
- System overhead: ~1.2GB
- **Total (with buffer)**: ~5.7-5.9GB (leaves ~2.1-2.3GB buffer) ✓
- **Base usage (idle)**: ~5.1GB (containers + system overhead)

### Memory Details

- Each LiteLLM worker uses ~460MB RAM (measured, not estimated)
- LiteLLM base process: ~320MB
- Open WebUI: ~602MB
- PostgreSQL: ~48MB (idle, can grow with usage)
- Nginx: ~6MB
- **Request buffers** (memory increases during active API calls):
  - LiteLLM: +200-400MB per worker during active requests
  - Open WebUI: +100-200MB during active chat sessions
  - PostgreSQL: +50-100MB during queries
- System overhead: 
  - ~1.2GB on typical Linux distributions (Ubuntu, Debian with desktop, Fedora)
  - ~0.7GB on lightweight distributions (Alpine, Debian minimal, Ubuntu Server minimal)
  - Includes OS, Docker daemons, and other system services

**Note**: All usage numbers above include buffers for active requests. Idle usage is lower, but you should plan for peak usage during active API calls.

**Note:** Resource limits are optimized based on PostgreSQL best practices and container memory constraints. PostgreSQL settings (`shared_buffers`, `effective_cache_size`, `work_mem`) are calculated based on available RAM. Memory usage is monitored and documented, but limits via `deploy.resources` are not supported in rootless Docker.

## Disk Space Requirements

The system uses several Docker volumes for persistent data storage:

### Base Storage (Required)

- **Docker Images**: ~3-4GB (PostgreSQL, LiteLLM, Open WebUI, Nginx)
- **System & Logs**: ~500MB-1GB (Docker logs, system files, configs)

### Persistent Data Volumes

| Volume | What's Stored | Small VPS | Medium VPS | Large VPS |
|--------|---------------|-----------|------------|-----------|
| **PostgreSQL** | Model configs, usage logs, metadata | 100-500MB | 500MB-2GB | 2-10GB |
| **Open WebUI** | Chat history, user data, files | 200MB-1GB | 1-5GB | 5-20GB+ |

### Storage Recommendations by Profile

**Small VPS (1-2 users, occasional use):**
- **Minimum**: 10GB
- **Recommended**: 15-20GB
- **Breakdown**:
  - Docker images: 4GB
  - PostgreSQL: 500MB-1GB (few models, minimal logging)
  - Open WebUI: 500MB-2GB (limited chat history)
  - Logs & system: 1GB
  - Buffer: 3-5GB

**Medium VPS (3-5 users, regular use):**
- **Minimum**: 20GB
- **Recommended**: 30-40GB
- **Breakdown**:
  - Docker images: 4GB
  - PostgreSQL: 1-3GB (multiple models, moderate logging)
  - Open WebUI: 2-8GB (active chat history, some file uploads)
  - Logs & system: 2GB
  - Buffer: 5-10GB

**Large VPS (10+ users, active use):**
- **Minimum**: 50GB
- **Recommended**: 100GB+
- **Breakdown**:
  - Docker images: 4GB
  - PostgreSQL: 5-15GB (many models, detailed logging, analytics)
  - Open WebUI: 10-50GB+ (extensive chat history, file uploads, RAG data)
  - Logs & system: 5GB
  - Buffer: 20GB+

### Growth Factors

Storage usage grows based on:
- **Number of users**: Each user's chat history and files
- **Chat activity**: More conversations = more storage
- **File uploads**: RAG documents, images, attachments
- **Model configurations**: More models = larger PostgreSQL database
- **Logging level**: Detailed logging increases PostgreSQL size
- **Retention period**: How long chat history is kept

### Storage Optimization Tips

1. **Regular cleanup**: Periodically remove old chat history in Open WebUI
2. **Log rotation**: Already configured (max 3-5 files per service)
3. **Monitor usage**: Check volumes with:
   ```bash
   docker system df                    # Overall Docker disk usage
   docker volume ls                    # List all volumes
   docker volume inspect <volume_name> # Check specific volume size
   ```

