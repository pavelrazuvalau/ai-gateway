# Glossary

<!--
Tags for AI agents:
- glossary
- terminology
- definitions
- concepts
- reference
-->

Definitions of key terms and concepts used in AI Gateway documentation.

## A

### AI Gateway

A bundled solution (similar to LAMP/XAMPP stacks) that combines LiteLLM, Open WebUI, PostgreSQL, and Nginx into a single, easy-to-configure package for working with language models.

**Related:** [Architecture](architecture.md), [Getting Started](getting-started.md)

## B

### Budget Profile

A configuration setting that defines spending limits for API usage. Available profiles:
- **test**: $15/month
- **prod**: $200/month
- **unlimited**: $1000/month

**Related:** [Configuration Guide](configuration.md#budget-profiles)

## D

### Docker Network

An isolated network created by Docker Compose for AI Gateway containers. Default name: `{project}_litellm-network`.

**Related:** [Architecture](architecture.md), [Troubleshooting](troubleshooting.md)

## L

### LiteLLM

A universal LLM proxy that provides a unified API interface for 100+ LLM providers. Core component of AI Gateway.

**Related:** [API for Agents](integrations/api-for-agents.md), [Getting Started](getting-started.md)

### LiteLLM Admin UI

Web interface for managing LiteLLM configuration, providers, models, and settings. Accessible at `http://localhost:PORT/ui`.

**Related:** [Getting Started](getting-started.md#step-32-add-providers), [Configuration Guide](configuration.md)

## M

### Master Key

A full-access API key for LiteLLM that provides administrative access. Should be kept secure and not exposed in client applications.

**Usage:**
- LiteLLM Admin UI login
- Administrative operations
- Direct API testing

**Security:** Never expose in client applications. Use Virtual Key instead.

**Related:** [Virtual Key Guide](configuration/virtual-key.md), [Security Guide](security.md)

### Model ID

The identifier used to reference a specific language model in API requests. Model IDs may differ from official provider names.

**Example:** `claude-sonnet-4-5`, `gpt-4o`, `gemini-pro`

**Note:** Always verify model IDs via `/v1/models` endpoint or LiteLLM Admin UI.

**Related:** [API for Agents](integrations/api-for-agents.md#supported-providers), [Getting Started](getting-started.md#step-5-configure-models)

## N

### Nginx

Reverse proxy server used by AI Gateway to route requests to different services. Provides:
- Single external port access
- Request routing
- Security isolation

**Related:** [Configuration Guide](configuration.md#port-configuration), [Nginx Configuration](nginx/README.md)

## O

### Open WebUI

Modern web interface for chatting with AI models. Automatically discovers models configured in LiteLLM.

**Related:** [Getting Started](getting-started.md), [Architecture](architecture.md)

## P

### PostgreSQL

Database used by LiteLLM to store configurations, usage data, and model information.

**Related:** [Architecture](architecture.md), [Configuration Guide](configuration.md)

### Provider

An LLM service provider (e.g., Anthropic, OpenAI, Google AI Studio) that offers language model APIs. AI Gateway supports 100+ providers through LiteLLM.

**Configuration:**
- Via LiteLLM Admin UI (recommended)
- Via environment variables in `.env`

**Related:** [API for Agents](integrations/api-for-agents.md#supported-providers), [Getting Started](getting-started.md#step-32-add-providers)

## R

### Resource Profile

A configuration setting that defines resource limits (RAM, CPU) for different deployment scenarios:
- **local**: No limits (desktop development)
- **small_vps**: 2GB RAM, 2 CPU cores
- **medium_vps**: 4GB RAM, 4 CPU cores (recommended)
- **large_vps**: 8GB+ RAM, 8 CPU cores

**Related:** [Configuration Guide](configuration.md#resource-profiles), [System Requirements](system-requirements.md)

## V

### Virtual Key

A restricted API key in LiteLLM that provides secure, limited access to the LiteLLM API. Recommended for application integrations.

**Features:**
- Restricted permissions
- More secure than Master Key
- Team-based access control
- Auditable usage
- Revocable without affecting Master Key

**Usage:**
- Open WebUI integration (required)
- Continue.dev integration
- Other application integrations
- Production deployments

**Related:** [Virtual Key Guide](configuration/virtual-key.md), [Security Guide](security.md)

## Common Abbreviations

### API
Application Programming Interface

### CLI
Command Line Interface

### CPU
Central Processing Unit

### HTTP
Hypertext Transfer Protocol

### HTTPS
Hypertext Transfer Protocol Secure

### LLM
Large Language Model

### RAM
Random Access Memory

### SSL
Secure Sockets Layer

### TLS
Transport Layer Security

### UI
User Interface

### VPS
Virtual Private Server

## Related Documentation

- **[Getting Started Guide](getting-started.md)** - Complete setup guide
- **[Configuration Guide](configuration.md)** - Configuration options
- **[Architecture](architecture.md)** - System architecture
- **[API for Agents](integrations/api-for-agents.md)** - API reference
- **[FAQ](FAQ.md)** - Frequently asked questions

