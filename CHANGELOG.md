# Changelog

All notable changes to AI Gateway will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Future features will be listed here)

---

## [0.0.1] - 2025-11-24

### Added
- Initial prototype release
- Setup script for Linux (tested), macOS and Windows (experimental, not fully tested)
- Support for LiteLLM, Open WebUI, PostgreSQL, and Nginx
- Resource profiles (Local, Small VPS, Medium VPS, Large VPS)
- Budget profiles (test, prod, unlimited)
- Interactive port configuration
- Docker Compose integration
- Nginx reverse proxy configuration
- SSL/HTTPS support via Let's Encrypt
- Admin UI for model and provider management
- Structured logging system
- Layered architecture (Core, Infrastructure, Application)
- Continue.dev integration script for VS Code extension
- Systemd service support for Linux

### Security
- Secure password and key generation
- File permissions management (600 for .env, 644 for config files)
- Security recommendations in SECURITY.md

### Known Limitations
- This is a prototype version with known limitations
- Scripts tested only on Linux; macOS and Windows support is experimental and not fully tested
- Rootless Docker support only in Proxmox VM (LXC not supported)
- GitHub Copilot integration attempted but not working
- Anthropic API Tier 1 has strict rate limits
- Not fully production-ready, more testing needed

[Unreleased]: https://github.com/pavelrazuvalau/ai-gateway/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/pavelrazuvalau/ai-gateway/releases/tag/v0.0.1

