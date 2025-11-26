# Nginx Configuration Examples

This directory contains example configurations for external Nginx servers.

## Files

### `external-nginx-example.conf`

Example configuration for an external Nginx server running on the host (outside Docker containers).

**Use this when you want to:**
- Add SSL/HTTPS support via Let's Encrypt (Certbot)
- Use your own domain name
- Have more control over SSL/TLS settings
- Proxy to the internal nginx container from AI Gateway

**Configuration steps:**

1. Replace `example.com` with your actual domain name
2. Replace `localhost:63345` with your server IP and the port where internal nginx is exposed
   - Check `docker-compose.override.yml` for nginx port mapping
   - Default internal nginx listens on port 80 inside container
   - External port is configured during setup (check `.env` file for `NGINX_HTTP_PORT`)
3. Place this file in your external Nginx configuration directory:
   - Linux: `/etc/nginx/sites-available/`
   - macOS: `/usr/local/etc/nginx/servers/` (if using Homebrew)
4. Configure SSL certificates:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```
5. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/
   ```
6. Test and reload:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

**Note:** This configuration is optimized for:
- Streaming responses (SSE)
- Large requests (up to 100MB)
- Tier 2 rate limits (RPM: 1,000, ITPM: up to 500k, OTPM: up to 50k)

## Internal Nginx Configuration

The internal nginx configuration (running inside Docker container) is located in:
- `nginx/nginx.conf` - main configuration
- `nginx/conf.d/` - site-specific configurations (auto-generated)

These files are managed by AI Gateway setup and should not be edited manually.

