# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------ | ----------------------- |
| Latest | :white_check_mark:      |

## Reporting a Vulnerability

If you discover a security vulnerability, **DO NOT** create a public Issue.

Instead:
1. Create a private Security Advisory on GitHub (Settings → Security → Security advisories → New draft security advisory)
2. Or send an email (specify your email)
3. Describe the vulnerability in detail
4. Provide steps to reproduce
5. Suggest a fix if possible

We will respond within 48 hours and fix the vulnerability as soon as possible.

## Security Recommendations

### For production use:

1. **Change all default passwords:**
   - `POSTGRES_PASSWORD` in `.env`
   - `UI_PASSWORD` in `.env`
   - `LITELLM_MASTER_KEY` in `.env`

2. **Use strong passwords:**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

3. **Configure firewall:**
   - Open only necessary ports
   - Use reverse proxy (Nginx) with TLS

4. **Regularly update:**
   - Docker images: `docker compose pull`
   - Python dependencies: `pip install -U -r requirements.txt`

5. **Don't commit secrets:**
   - `.env` file should be in `.gitignore`
   - Use `env.example` for templates

6. **Use HTTPS:**
   - Configure SSL via Let's Encrypt
   - Use `USE_SSL=yes` in settings

7. **Limit access:**
   - Use VPN or firewall for Admin UI access
   - Don't expose Admin UI publicly without authentication

## Known Limitations

- Admin UI doesn't have built-in authentication (only master key is used)
- For production, it's recommended to use reverse proxy with additional authentication
