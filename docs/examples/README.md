# Examples

<!--
Tags for AI agents:
- examples
- code-examples
- use-cases
- integration-examples
- configuration-examples
- python
- javascript
- curl
-->

This directory contains practical examples for using AI Gateway in various scenarios.

## Quick Links

- **[Python Examples](python-basic.md)** - Basic Python integration examples
- **[JavaScript Examples](javascript-basic.md)** - Basic JavaScript/TypeScript examples
- **[Integration Examples](integration-examples.md)** - Integration with popular tools and frameworks
- **[Configuration Examples](configuration-examples.md)** - Example configurations for different scenarios

## Example Categories

### Basic Usage

- **Python**: Simple chat completions, streaming, error handling
- **JavaScript**: Browser and Node.js examples
- **cURL**: Command-line examples for testing

### Integrations

- **LangChain**: Integration with LangChain framework
- **LlamaIndex**: Integration with LlamaIndex
- **OpenAI SDK**: Using OpenAI SDK with AI Gateway
- **Custom Applications**: Building custom applications

### Configuration

- **Development Setup**: Minimal configuration for local development
- **Production Setup**: Production-ready configuration examples
- **Multi-Provider**: Configuration for multiple providers
- **Budget Control**: Budget and rate limiting examples

## Getting Started

1. **Set up AI Gateway**: Follow [Getting Started Guide](../getting-started.md)
2. **Get your Virtual Key**: See [Virtual Key Configuration](../configuration/virtual-key.md)
3. **Choose an example**: Browse examples by category above
4. **Run the example**: Copy and adapt the code to your needs

## Prerequisites

All examples assume:
- AI Gateway is running (see [Getting Started](../getting-started.md))
- Virtual Key is configured (see [Virtual Key Configuration](../configuration/virtual-key.md))
- At least one model is configured in LiteLLM Admin UI

> ✅ **Verified:** All examples have been tested on a real AI Gateway installation and work correctly.

## Base URL

Examples use the default Nginx configuration:
- **API Base**: `http://localhost:PORT/api/litellm/v1`
- Replace `PORT` with your configured port (check `.env` for `NGINX_HTTP_PORT`)

For configuration without Nginx:
- **API Base**: `http://localhost:4000/v1`

## Authentication

All examples use Virtual Key authentication:
```bash
# Get your Virtual Key
grep VIRTUAL_KEY .env
```

Use the Virtual Key in the `Authorization: Bearer` header.

## Related Documentation

- **[API for Agents](../integrations/api-for-agents.md)** - Complete API reference
- **[Configuration Guide](../configuration.md)** - Configuration options
- **[Troubleshooting](../troubleshooting.md)** - Common issues and solutions

