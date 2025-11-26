# API for AI Agents

<!--
Tags for AI agents:
- api-documentation
- integration
- authentication
- endpoints
- local-development
- openapi-spec
- code-examples
- python
- javascript
- curl
- providers
- model-configuration
-->

Complete guide for AI agents and automated systems to integrate with AI Gateway. This documentation covers API endpoints, authentication, local development, and best practices.

## Quick Links

- **[Authentication](#authentication)** - Virtual Key and Master Key
- **[API Endpoints](#api-endpoints)** - Core endpoints and examples
- **[Local Development](#local-development-and-testing)** - Setup for local testing
- **[OpenAPI Specification](#getting-openapi-specification)** - Get OpenAPI spec
- **[Supported Providers](#supported-providers)** - Provider configuration
- **[Examples](../examples/README.md)** - Code examples in Python, JavaScript

**Related Documentation:**
- [Getting Started](../getting-started.md) - Initial setup
- [Configuration Guide](../configuration.md) - Configuration options
- [Troubleshooting](../troubleshooting.md) - API issues

## Overview

AI Gateway exposes a unified LiteLLM API that provides access to multiple LLM providers through a single interface. The API follows the OpenAI-compatible format, making it easy to integrate with existing tools and frameworks.

### Base URLs

**With Nginx (default):**
- API Base: `http://localhost:PORT/api/litellm/v1`
- Example: `http://localhost:3000/api/litellm/v1`

**Without Nginx:**
- API Base: `http://localhost:4000/v1`
- Example: `http://localhost:4000/v1`

**From Docker network (internal):**
- API Base: `http://litellm:4000/v1`

> **Note:** Replace `localhost:PORT` with your configured port. Check `.env` file for `NGINX_HTTP_PORT` (with Nginx) or `LITELLM_EXTERNAL_PORT` (without Nginx).

## Authentication

AI Gateway uses **Bearer token authentication** with Virtual Keys or Master Key.

### Virtual Key (Recommended)

Virtual Keys provide better security and access control. They are created in LiteLLM Admin UI and stored in `.env` file.

**Get Virtual Key:**
```bash
# From .env file
grep VIRTUAL_KEY .env
# Output: VIRTUAL_KEY=sk-xxxxxxxxxxxxx
```

**Use in requests:**
```bash
curl -H "Authorization: Bearer sk-xxxxxxxxxxxxx" \
  http://localhost:3000/api/litellm/v1/models
```

### Master Key (Not Recommended)

Master Key provides full access but is less secure. Use only for testing or when Virtual Key is not available.

**Get Master Key:**
```bash
# From .env file
grep LITELLM_MASTER_KEY .env
# Output: LITELLM_MASTER_KEY=sk-xxxxxxxxxxxxx
```

> ⚠️ **Security Warning:** Never expose Master Key in client applications. Always use Virtual Keys for API access.

## API Endpoints

AI Gateway supports all standard OpenAI-compatible endpoints through LiteLLM. The API follows the OpenAI format: https://platform.openai.com/docs/api-reference

### Core Endpoints

#### List Models
Get list of available models.

**Endpoint:** `GET /v1/models`

**Example:**
```bash
curl http://localhost:3000/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY"
```

**Response:**
```json
{
  "data": [
    {
      "id": "claude-sonnet-4-5",
      "object": "model",
      "created": 1234567890,
      "owned_by": "anthropic"
    },
    {
      "id": "gpt-4o",
      "object": "model",
      "created": 1234567890,
      "owned_by": "openai"
    }
  ],
  "object": "list"
}
```

#### Chat Completions
Generate chat completions (most common endpoint).

**Endpoint:** `POST /v1/chat/completions`

**Example:**
```bash
curl http://localhost:3000/api/litellm/v1/chat/completions \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "claude-sonnet-4-5",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 12,
    "total_tokens": 22
  }
}
```

#### Streaming Chat Completions
Get streaming responses for real-time applications.

**Endpoint:** `POST /v1/chat/completions` (with `stream: true`)

**Example:**
```bash
curl http://localhost:3000/api/litellm/v1/chat/completions \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": true
  }'
```

**Response (Server-Sent Events):**
```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"claude-sonnet-4-5","choices":[{"index":0,"delta":{"content":"Once"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"claude-sonnet-4-5","choices":[{"index":0,"delta":{"content":" upon"},"finish_reason":null}]}

data: [DONE]
```

### Additional Endpoints

AI Gateway supports all standard OpenAI endpoints:

- **Completions:** `POST /v1/completions` - Text completions
- **Embeddings:** `POST /v1/embeddings` - Generate embeddings
- **Audio:** `POST /v1/audio/transcriptions` - Transcribe audio
- **Audio:** `POST /v1/audio/translations` - Translate audio
- **Images:** `POST /v1/images/generations` - Generate images
- **Moderations:** `POST /v1/moderations` - Content moderation
- **Files:** `GET /v1/files`, `POST /v1/files`, `DELETE /v1/files/{file_id}` - File operations
- **Assistants:** `POST /v1/assistants`, `GET /v1/assistants/{assistant_id}` - Assistants API
- **Threads:** `POST /v1/threads`, `GET /v1/threads/{thread_id}` - Threads API
- **Messages:** `POST /v1/threads/{thread_id}/messages` - Messages API

> **Note:** Not all providers support all endpoints. Check provider documentation for supported features.

## Supported Providers

AI Gateway uses LiteLLM, which supports **100+ LLM providers**. This section covers the most popular providers and how to configure them.

> 📚 **Complete Provider List:** See [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers) for the full list of 100+ supported providers, setup instructions, and provider-specific details.

### Provider Configuration

Providers can be configured in two ways:

1. **Via LiteLLM Admin UI (Recommended):**
   - Open http://localhost:4000/ui
   - Go to "Providers" section
   - Add provider and API key
   - See [Getting Started Guide](../getting-started.md#step-32-add-providers) for details

2. **Via Environment Variables:**
   - Add API key to `.env` file
   - Format: `{PROVIDER}_API_KEY=your-key-here`
   - Example: `ANTHROPIC_API_KEY=sk-ant-...`

### Popular Providers

#### Anthropic (Claude)
- **Environment Variable:** `ANTHROPIC_API_KEY`
- **Get API Key:** https://console.anthropic.com/
- **LiteLLM Docs:** https://docs.litellm.ai/docs/providers/anthropic
- **Model IDs:** Check LiteLLM docs or `/v1/models` endpoint for exact IDs
  - Common patterns: `claude-3-5-sonnet`, `claude-3-opus`, `claude-3-haiku`, `claude-sonnet-4-5`
  - ⚠️ **Note:** Model IDs may differ from official names - always verify via API
- ⚠️ **Note:** Tier 1 has strict rate limits - Tier 2+ recommended

#### OpenAI (GPT)
- **Environment Variable:** `OPENAI_API_KEY`
- **Get API Key:** https://platform.openai.com/api-keys
- **Models:** `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Docs:** https://docs.litellm.ai/docs/providers/openai

#### Google AI Studio (Gemini)
- **Environment Variable:** `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- **Get API Key:** https://makersuite.google.com/app/apikey
- **Models:** `gemini-pro`, `gemini-pro-vision`
- **Docs:** https://docs.litellm.ai/docs/providers/google_ai_studio

#### Azure OpenAI
- **Environment Variables:** `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION`
- **Get API Key:** Azure Portal
- **Models:** Same as OpenAI (deployed on Azure)
- **Docs:** https://docs.litellm.ai/docs/providers/azure_openai

#### Groq
- **Environment Variable:** `GROQ_API_KEY`
- **Get API Key:** https://console.groq.com/keys
- **Models:** Fast inference for open models
- **Docs:** https://docs.litellm.ai/docs/providers/groq

#### Mistral AI
- **Environment Variable:** `MISTRAL_API_KEY`
- **Get API Key:** https://console.mistral.ai/
- **Models:** `mistral-large`, `mistral-medium`, `mistral-small`
- **Docs:** https://docs.litellm.ai/docs/providers/mistral

#### Deepseek
- **Environment Variable:** `DEEPSEEK_API_KEY`
- **Get API Key:** https://deepseek.com/
- **Models:** `deepseek-chat`, `deepseek-coder`
- **Docs:** https://docs.litellm.ai/docs/providers/deepseek

#### Together AI
- **Environment Variable:** `TOGETHER_API_KEY`
- **Get API Key:** https://together.ai/
- **Models:** Various open models
- **Docs:** https://docs.litellm.ai/docs/providers/together

#### Perplexity AI
- **Environment Variable:** `PERPLEXITY_API_KEY`
- **Get API Key:** https://www.perplexity.ai
- **Models:** `pplx-70b-online`, `pplx-7b-online`
- **Docs:** https://docs.litellm.ai/docs/providers/perplexity

#### xAI (Grok)
- **Environment Variable:** `XAI_API_KEY`
- **Get API Key:** https://docs.x.ai/docs
- **Models:** `grok-beta`
- **Docs:** https://docs.litellm.ai/docs/providers/xai

#### OpenRouter
- **Environment Variable:** `OPENROUTER_API_KEY`
- **Get API Key:** https://openrouter.ai/
- **Models:** Access to multiple providers through one API
- **Docs:** https://docs.litellm.ai/docs/providers/openrouter

#### Local Models (No API Key Required)

**Ollama:**
- **Setup:** Local deployment, no API key
- **Models:** Any model supported by Ollama
- **Docs:** https://docs.litellm.ai/docs/providers/ollama

**LM Studio:**
- **Setup:** Local deployment, no API key
- **Models:** Any model supported by LM Studio
- **Docs:** https://docs.litellm.ai/docs/providers/lm_studio

### Checking Available Models

> ⚠️ **IMPORTANT:** Model IDs in LiteLLM may differ from provider's official names and can be customized. **Always check actual model IDs** using the methods below, as they may not match examples in documentation.

After configuring providers, check available models:

```bash
# List all available models (recommended method)
curl http://localhost:3000/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" | jq '.data[].id'

# Or format as table
curl http://localhost:3000/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" | jq -r '.data[] | "\(.id) - \(.owned_by)"'
```

Or via Python:
```python
import requests

response = requests.get(
    "http://localhost:3000/api/litellm/v1/models",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
models = response.json()['data']
for model in models:
    print(f"{model['id']} - {model.get('owned_by', 'unknown')}")
```

**Alternative Methods:**
- **LiteLLM Admin UI:** Go to Models section to see all configured models
- **Provider Documentation:** Check [LiteLLM Providers Docs](https://docs.litellm.ai/docs/providers) for each provider's specific model ID formats

### Provider-Specific Notes

- **Rate Limits:** Each provider has different rate limits. Check provider documentation.
- **Model IDs:** ⚠️ **CRITICAL** - Model IDs may vary by provider and can differ from official names. 
  - Always check `/v1/models` endpoint for actual IDs in your setup
  - Model IDs can be customized in LiteLLM Admin UI
  - Check [LiteLLM Providers Docs](https://docs.litellm.ai/docs/providers) for provider-specific formats
- **Costs:** Different providers have different pricing. Check provider pricing pages.
- **Features:** Not all providers support all features (e.g., streaming, function calling).

> **For complete provider information:** See [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers) for:
> - Full list of 100+ providers
> - Provider-specific setup instructions
> - Environment variable names
> - Model ID formats
> - Rate limits and pricing

## Code Examples

### Python

```python
import requests
import os

# Configuration
API_BASE = "http://localhost:3000/api/litellm/v1"
API_KEY = os.getenv("VIRTUAL_KEY", "your-virtual-key-here")

# List models
response = requests.get(
    f"{API_BASE}/models",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
models = response.json()
print(f"Available models: {[m['id'] for m in models['data']]}")

# Chat completion
response = requests.post(
    f"{API_BASE}/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "claude-sonnet-4-5",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
)
result = response.json()
print(f"Response: {result['choices'][0]['message']['content']}")
```

### JavaScript/TypeScript

```javascript
const API_BASE = "http://localhost:3000/api/litellm/v1";
const API_KEY = process.env.VIRTUAL_KEY || "your-virtual-key-here";

// List models
async function listModels() {
  const response = await fetch(`${API_BASE}/models`, {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  });
  const data = await response.json();
  console.log("Available models:", data.data.map(m => m.id));
}

// Chat completion
async function chatCompletion(message) {
  const response = await fetch(`${API_BASE}/chat/completions`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-5",
      messages: [
        { role: "user", content: message }
      ],
      temperature: 0.7,
      max_tokens: 1000
    })
  });
  const result = await response.json();
  return result.choices[0].message.content;
}
```

### Using OpenAI SDK (Compatible)

Since AI Gateway uses OpenAI-compatible API, you can use OpenAI SDKs:

**Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3000/api/litellm/v1",
    api_key="your-virtual-key-here"
)

response = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

**JavaScript:**
```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:3000/api/litellm/v1',
  apiKey: 'your-virtual-key-here'
});

const response = await client.chat.completions.create({
  model: 'claude-sonnet-4-5',
  messages: [{ role: 'user', content: 'Hello!' }]
});
console.log(response.choices[0].message.content);
```

## Local Development and Testing

AI agents can set up and test AI Gateway locally for development and integration testing.

### Prerequisites

- **Docker**: 20.10+ (Docker Compose v2)
- **Python**: 3.8+ (for setup scripts)
- **RAM**: 3GB minimum (4GB recommended)
- **Disk**: 10GB minimum

### Step 1: Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd ai-gateway

# Run setup
./setup.sh  # Linux/macOS
# or
setup.bat   # Windows
```

**Setup will:**
- Configure resource profile
- Set up ports
- Generate `.env` file
- Create `config.yaml`
- Generate `docker-compose.override.yml`

### Step 2: Configure Environment

**Minimal `.env` for local testing:** ✅ **ПРОВЕРЕНО**

> ✅ **Подтверждено:** Минимальный набор переменных проверен на реальном сервере (2025-11-26)

```bash
# ══════════════════════════════════════════════════════════
# ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ (для запуска setup и start)
# ══════════════════════════════════════════════════════════

# Master Key (обязательно, должен начинаться с "sk-")
# Генерация: openssl rand -base64 32
LITELLM_MASTER_KEY=sk-your-master-key-here

# PostgreSQL (обязательно)
POSTGRES_USER=litellm
POSTGRES_PASSWORD=litellm_password  # Минимум 8 символов
POSTGRES_DB=litellm
POSTGRES_PORT=5432

# ══════════════════════════════════════════════════════════
# ОПЦИОНАЛЬНЫЕ ПЕРЕМЕННЫЕ (можно оставить пустыми)
# ══════════════════════════════════════════════════════════

# UI Credentials (опционально, по умолчанию: admin/change_this_password_123)
UI_USERNAME=admin
UI_PASSWORD=change_this_password_123  # Минимум 8 символов, если указан

# WebUI Secret Key (опционально, минимум 16 символов, если указан)
WEBUI_SECRET_KEY=

# API Keys провайдеров (НЕ обязательны для запуска!)
# Можно добавить позже через LiteLLM Admin UI
# ANTHROPIC_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here
# GEMINI_API_KEY=your-key-here
# GROQ_API_KEY=your-key-here

# Virtual Key (создается после первого запуска)
# VIRTUAL_KEY=sk-xxxxxxxxxxxxx

# Порты (настраиваются автоматически при setup)
# LITELLM_EXTERNAL_PORT=4000
# NGINX_HTTP_PORT=63345
# USE_NGINX=yes
```

**Важно:**
- ✅ API ключи провайдеров **НЕ обязательны** для запуска setup/start
- ✅ Можно запустить систему без провайдеров и добавить их позже через LiteLLM Admin UI
- ✅ PostgreSQL **обязателен** - система не работает без него (in-memory не поддерживается)
- ✅ Минимальные требования: 3GB RAM, Docker 20.10+, Python 3.8+

**Isolation from other projects:** ✅ **ПРОВЕРЕНО**

> ✅ **Подтверждено:** Изоляция работает автоматически через Docker Compose (проверено на сервере 2025-11-26)

1. **Docker network (автоматическая изоляция):**
   - ✅ AI Gateway создает отдельную Docker network автоматически
   - ✅ Имя сети: `{project}_litellm-network` (например, `ai-gateway_litellm-network`)
   - ✅ Тип: `bridge` - изолированная сеть для проекта
   - ✅ Проверка: `docker network ls | grep litellm`

2. **Уникальные имена контейнеров:**
   - ✅ Фиксированные имена: `litellm-proxy`, `litellm-postgres`, `open-webui`, `litellm-nginx`
   - ✅ Имена уникальны для проекта (Docker Compose добавляет префикс проекта)
   - ✅ Проверка: `docker ps --format "table {{.Names}}\t{{.Image}}"`

3. **Избежание конфликтов портов:**
   - ✅ Во время setup можно выбрать "random high ports"
   - ✅ Порты в диапазоне 49152-65535
   - ✅ Порты настраиваются в `.env` и `docker-compose.override.yml`
   - ✅ Проверка: `docker compose ps` показывает маппинг портов

4. **Отдельный `.env` файл:**
   - ✅ `.env` специфичен для проекта (не коммитится в git)
   - ✅ Каждый проект имеет свою конфигурацию
   - ✅ Права доступа: 600 (только владелец)

### Step 3: Start Locally

```bash
# Start containers
./start.sh  # Linux/macOS
# or
start.bat   # Windows
```

**Wait for containers to be healthy:**
- Setup waits for health checks automatically
- Containers are ready when you see: "✅ Containers started and healthy!"

### Step 4: Create Virtual Key

```bash
# Create Virtual Key
./virtual-key.sh  # Linux/macOS
# or
virtual-key.bat   # Windows
```

Virtual Key will be saved to `.env` file automatically.

### Step 5: Test API

```bash
# Test API endpoint
curl http://localhost:3000/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY"

# Or if using Master Key (not recommended)
curl http://localhost:3000/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_MASTER_KEY"
```

### Step 6: Verify System Health ✅ **ЧЕКЛИСТ ПРОВЕРКИ**

**После setup:**
```bash
# 1. Проверить наличие файлов
ls -la .env config.yaml docker-compose.override.yml

# 2. Проверить права доступа (должно быть 600)
stat -c "%a %n" .env config.yaml docker-compose.override.yml

# 3. Проверить обязательные переменные в .env
grep -E "^LITELLM_MASTER_KEY=|^POSTGRES_" .env
```

**После start:**
```bash
# 1. Проверить статус контейнеров (все должны быть "Up" и "healthy")
docker compose ps

# 2. Проверить health checks
docker compose ps --format json | python3 -m json.tool | grep -A 2 Health
# Ожидаемый результат: "healthy" для postgres, litellm, open-webui

# 3. Проверить API доступность (через Nginx)
curl -s http://localhost:PORT/api/litellm/v1/models \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" | python3 -m json.tool | head -20

# 4. Проверить API доступность (напрямую к LiteLLM, если порт exposed)
LITELLM_PORT=$(grep LITELLM_EXTERNAL_PORT .env | cut -d= -f2)
VIRTUAL_KEY=$(grep VIRTUAL_KEY .env | cut -d= -f2)
curl -s http://localhost:${LITELLM_PORT}/v1/models \
  -H "Authorization: Bearer ${VIRTUAL_KEY}" | python3 -m json.tool | head -20

# 5. Проверить OpenAPI spec (внутри контейнера)
docker exec litellm-proxy python3 -c "import requests; r = requests.get('http://localhost:4000/openapi.json'); print('✅ OpenAPI spec доступен' if r.status_code == 200 else '❌ OpenAPI spec недоступен'); print(f'Размер: {len(r.text)} байт'); data=r.json() if r.status_code == 200 else {}; print(f'Endpoints: {len(data.get(\"paths\", {}))}') if data else None"
# Ожидаемый результат: ✅ OpenAPI spec доступен, Размер: ~776KB, Endpoints: 330

# 6. Проверить OpenAPI spec (через внешний порт с Master Key)
LITELLM_PORT=$(grep LITELLM_EXTERNAL_PORT .env | cut -d= -f2)
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env | cut -d= -f2)
curl -s http://localhost:${LITELLM_PORT}/openapi.json \
  -H "Authorization: Bearer ${MASTER_KEY}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'OpenAPI {data.get(\"openapi\")}, {len(data.get(\"paths\", {}))} endpoints')"
# Ожидаемый результат: OpenAPI 3.1.0, 330 endpoints

# 7. Проверить health check
docker exec litellm-proxy python3 -c "import requests; r = requests.get('http://localhost:4000/health/liveliness'); print('✅ Health check OK' if r.status_code == 200 else f'❌ Health check failed: {r.status_code}'); print(f'Response: {r.text[:50]}')"
# Ожидаемый результат: ✅ Health check OK, Response: I'm alive!

# 8. Проверить логи на ошибки
docker compose logs | grep -i error | tail -20

# 9. Проверить Docker network
docker network ls | grep litellm
docker network inspect ai-gateway_litellm-network 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Network: {data[0][\"Name\"]}'); print(f'Containers: {len(data[0][\"Containers\"])}')"
# Ожидаемый результат: Network: ai-gateway_litellm-network, Containers: 4
```

### Troubleshooting Local Setup

**Port conflicts:**
```bash
# Check what's using the port
sudo lsof -i :3000  # Linux/macOS
netstat -ano | findstr :3000  # Windows

# Solution: Re-run setup and choose different ports
./setup.sh
```

**Containers won't start:**
```bash
# Check container status
docker compose ps

# View logs
docker compose logs

# Restart
./stop.sh
./start.sh
```

**Virtual Key creation fails:**
- Wait 45+ seconds after container start (LiteLLM needs time to initialize)
- Check LiteLLM logs: `docker compose logs litellm-proxy`
- Create manually via LiteLLM Admin UI: http://localhost:4000/ui

## Getting OpenAPI Specification

OpenAPI specification provides complete API documentation in machine-readable format. This is useful for:
- Understanding all available endpoints
- Generating API clients automatically
- Validating requests/responses
- API documentation tools

### Method 1: From Running Container ✅ **ПРОВЕРЕНО**

**Get OpenAPI spec from LiteLLM container:**

> ✅ **Подтверждено:** OpenAPI spec доступен по умолчанию в контейнере LiteLLM (проверено на сервере 2025-11-26)

```bash
# Method 1: Via HTTP endpoint using Python (curl не установлен в контейнере)
docker exec litellm-proxy python3 -c "import requests; r = requests.get('http://localhost:4000/openapi.json'); print(r.text if r.status_code == 200 else f'Error: {r.status_code}')" > openapi.json

# Method 2: Via wget (если доступен)
docker exec litellm-proxy wget -qO- http://localhost:4000/openapi.json > openapi.json

# Method 3: Check OpenAPI module and Swagger UI files
docker exec litellm-proxy find /app -name "*openapi*" -o -name "*swagger*"
# Результат: /app/litellm/proxy/swagger/, /app/litellm/proxy/common_utils/custom_openapi_spec.py

# Проверка доступности
docker exec litellm-proxy python3 -c "import requests; r = requests.get('http://localhost:4000/openapi.json'); print(f'Status: {r.status_code}, Size: {len(r.text)} bytes, Content-Type: {r.headers.get(\"Content-Type\")}')"
# Ожидаемый результат: Status: 200, Size: ~776KB, Content-Type: application/json
```

**Формат:** OpenAPI 3.1.0, JSON, размер ~776KB, **330 endpoints** ✅ **ПРОВЕРЕНО**

> ✅ **Подтверждено на сервере (2025-11-26):**
> - OpenAPI version: 3.1.0
> - Info title: LiteLLM API
> - Paths count: 330 endpoints
> - Доступен через: `http://localhost:4000/openapi.json` (внутри контейнера) или через внешний порт с аутентификацией

### Method 2: From Host (if port is exposed) ✅ **ПРОВЕРЕНО**

> ✅ **Подтверждено:** OpenAPI spec доступен через внешний порт с Master Key (проверено на сервере 2025-11-26)

```bash
# If LiteLLM port is exposed (without Nginx or via separate port)
# Get port from .env: LITELLM_EXTERNAL_PORT
LITELLM_PORT=$(grep LITELLM_EXTERNAL_PORT .env | cut -d= -f2)
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env | cut -d= -f2)

curl http://localhost:${LITELLM_PORT}/openapi.json \
  -H "Authorization: Bearer ${MASTER_KEY}" \
  -o openapi.json

# Verify spec
python3 -c "import json; data=json.load(open('openapi.json')); print(f'OpenAPI {data.get(\"openapi\")}, {len(data.get(\"paths\", {}))} endpoints')"
# Ожидаемый результат: OpenAPI 3.x, ~100+ endpoints
```

**Важно:** 
- ✅ Требуется аутентификация (Master Key или Virtual Key)
- ✅ Формат: OpenAPI 3.x, JSON
- ✅ Размер: ~776KB

### Method 3: Generate from LiteLLM Documentation

LiteLLM follows OpenAI API format. You can use OpenAI's OpenAPI spec as a reference:

- **OpenAI OpenAPI Spec:** https://github.com/openai/openai-openapi
- **LiteLLM Documentation:** https://docs.litellm.ai/

### Using OpenAPI Spec

**Generate API client (Python):**
```bash
# Install openapi-generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o ./generated-client
```

**Generate API client (TypeScript):**
```bash
# Generate TypeScript client
openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o ./generated-client
```

**Validate requests:**
```python
from openapi_spec_validator import validate_spec

# Load and validate spec
with open('openapi.json') as f:
    spec = json.load(f)
    validate_spec(spec)
```

## Rate Limits

Rate limits depend on:
- **Provider limits:** Each LLM provider has its own rate limits
- **Resource profile:** Higher profiles allow more concurrent requests
- **Budget profile:** Budget limits may restrict usage

**Check current limits:**
- View in LiteLLM Admin UI: http://localhost:4000/ui
- Check budget settings in `.env`: `BUDGET_PROFILE=test|prod|unlimited`

**Best practices:**
- Use retry logic with exponential backoff
- Implement request queuing for high-volume applications
- Monitor usage in LiteLLM Admin UI
- Use Virtual Keys with specific model/endpoint restrictions

## Best Practices

### 1. Use Virtual Keys
- ✅ Create separate Virtual Keys for different applications
- ✅ Restrict Virtual Keys to specific models/endpoints
- ❌ Never use Master Key in client applications

### 2. Error Handling
```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(...)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed - check API key")
    elif e.response.status_code == 429:
        print("Rate limit exceeded - retry later")
    else:
        print(f"API error: {e}")
except RequestException as e:
    print(f"Request failed: {e}")
```

### 3. Connection Pooling
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

### 4. Streaming for Long Responses
```python
import requests

response = requests.post(
    f"{API_BASE}/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"model": "claude-sonnet-4-5", "messages": [...], "stream": True},
    stream=True
)

for line in response.iter_lines():
    if line:
        # Parse Server-Sent Events
        if line.startswith(b"data: "):
            data = line[6:]  # Remove "data: " prefix
            if data == b"[DONE]":
                break
            chunk = json.loads(data)
            # Process chunk
```

### 5. Model Selection
- Check available models before making requests
- Use appropriate models for tasks (e.g., Haiku for simple tasks, Opus for complex)
- Consider cost vs. quality trade-offs

## Troubleshooting

### Authentication Errors

**401 Unauthorized:**
- Check API key is correct
- Verify Virtual Key exists in `.env`
- Ensure `Authorization: Bearer` header format is correct

### Connection Errors

**Connection refused:**
- Verify containers are running: `docker compose ps`
- Check port configuration in `.env`
- Ensure firewall allows connections

**Timeout errors:**
- Check LiteLLM logs: `docker compose logs litellm-proxy`
- Verify provider API keys are valid
- Check network connectivity

### Model Not Found

**404 Model not found:**
- Verify model is configured in LiteLLM Admin UI
- Check model ID matches provider's format
- Ensure provider API key is valid

### Rate Limit Errors

**429 Too Many Requests:**
- Implement exponential backoff
- Reduce request frequency
- Check budget limits in `.env`

## Additional Resources

- **LiteLLM Documentation:** https://docs.litellm.ai/
- **OpenAI API Reference:** https://platform.openai.com/docs/api-reference
- **Getting Started Guide:** [Getting Started](../getting-started.md)
- **Configuration Guide:** [Configuration](../configuration.md)
- **Troubleshooting:** [Troubleshooting](../troubleshooting.md)

---

**For questions or issues, check the [Troubleshooting Guide](../troubleshooting.md) or create an issue on GitHub.**

