# Changelog

All notable changes to AI Gateway will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Future features will be listed here)

---

## [0.0.2] - 2025-11-24

### Fixed
- Updated memory calculations based on real measurements from production deployment
- Corrected worker memory usage from 400MB to 460MB per worker
- Updated system overhead estimates from ~1GB to ~1.2GB
- Fixed SMALL_VPS profile calculations (actual usage ~2.3-2.5GB, not 2.8GB)

### Added
- Request buffer calculations in all resource profiles
- Comprehensive memory troubleshooting section in README
- Lightweight Linux distribution recommendations for Small VPS users

### Changed
- Updated all resource profile memory calculations with verified measurements
- Improved SMALL_VPS documentation with accurate usage numbers
- Enhanced memory requirements documentation with request buffer details
- Updated minimum RAM recommendation from 2GB to 3GB (with warnings for 2GB systems)

### Documentation
- Added detailed memory breakdown per service
- Updated Resource Profiles section with real measurements (2025-11-24)
- Added troubleshooting section for OOM errors

### Removed
- Memory limits from docker-compose.yml (deploy.resources not supported in rootless Docker)

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

[Unreleased]: https://github.com/pavelrazuvalau/ai-gateway/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/pavelrazuvalau/ai-gateway/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/pavelrazuvalau/ai-gateway/releases/tag/v0.0.1

