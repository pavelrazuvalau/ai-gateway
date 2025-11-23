# Changelog

All notable changes to AI Gateway will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Future features will be listed here)

---

## [0.1.0] - 2025-01-XX

### Added
- Initial release
- Setup script for Linux/macOS and Windows
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

### Changed
- All user-facing text translated to English
- Improved formatting and consistency across scripts
- Simplified update mode when using existing .env

### Security
- Secure password and key generation
- File permissions management (600 for .env, 644 for config files)
- Security recommendations in SECURITY.md

[Unreleased]: https://github.com/yourusername/ai-gateway/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/ai-gateway/releases/tag/v0.1.0

