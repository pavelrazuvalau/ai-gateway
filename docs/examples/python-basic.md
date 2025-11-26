# Python Examples

<!--
Tags for AI agents:
- python
- code-examples
- python-sdk
- openai-sdk
- chat-completions
- streaming
-->

Basic Python examples for integrating with AI Gateway.

> ✅ **Verified:** Examples have been tested on a real AI Gateway installation (2025-11-26).

## Prerequisites

Install required packages:
```bash
pip install openai requests
```

## Basic Setup

```python
import os
from openai import OpenAI

# Get Virtual Key from environment or .env file
VIRTUAL_KEY = os.getenv("VIRTUAL_KEY", "sk-your-virtual-key-here")
BASE_URL = "http://localhost:3000/api/litellm/v1"  # Replace with your port

# Initialize OpenAI client (compatible with AI Gateway)
client = OpenAI(
    api_key=VIRTUAL_KEY,
    base_url=BASE_URL
)
```

## Example 1: Simple Chat Completion

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-virtual-key-here",
    base_url="http://localhost:3000/api/litellm/v1"
)

response = client.chat.completions.create(
    model="claude-sonnet-4-5",  # Replace with your model ID
    messages=[
        {"role": "user", "content": "Hello! Explain quantum computing in one sentence."}
    ],
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)
```

## Example 2: Streaming Chat Completion

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-virtual-key-here",
    base_url="http://localhost:3000/api/litellm/v1"
)

stream = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=[
        {"role": "user", "content": "Write a short story about a robot."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()  # New line at the end
```

## Example 3: Multi-Turn Conversation

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-virtual-key-here",
    base_url="http://localhost:3000/api/litellm/v1"
)

# Maintain conversation history
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"}
]

# First turn
response = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=messages
)
assistant_message = response.choices[0].message.content
print(f"Assistant: {assistant_message}")

# Add assistant response to history
messages.append({"role": "assistant", "content": assistant_message})

# Second turn
messages.append({"role": "user", "content": "Can you give me an example?"})
response = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=messages
)
print(f"Assistant: {response.choices[0].message.content}")
```

## Example 4: Error Handling

```python
from openai import OpenAI
from openai import APIError, RateLimitError

client = OpenAI(
    api_key="sk-your-virtual-key-here",
    base_url="http://localhost:3000/api/litellm/v1"
)

try:
    response = client.chat.completions.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except APIError as e:
    print(f"API error: {e.status_code} - {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Example 5: List Available Models

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-virtual-key-here",
    base_url="http://localhost:3000/api/litellm/v1"
)

models = client.models.list()
for model in models.data:
    print(f"Model ID: {model.id}, Owner: {model.owned_by}")
```

## Example 6: Using Requests Library (Alternative)

```python
import requests
import json

BASE_URL = "http://localhost:3000/api/litellm/v1"
VIRTUAL_KEY = "sk-your-virtual-key-here"

headers = {
    "Authorization": f"Bearer {VIRTUAL_KEY}",
    "Content-Type": "application/json"
}

# Chat completion
response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json={
        "model": "claude-sonnet-4-5",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "temperature": 0.7
    }
)

if response.status_code == 200:
    data = response.json()
    print(data["choices"][0]["message"]["content"])
else:
    print(f"Error: {response.status_code} - {response.text}")
```

## Example 7: Streaming with Requests

```python
import requests
import json

BASE_URL = "http://localhost:3000/api/litellm/v1"
VIRTUAL_KEY = "sk-your-virtual-key-here"

headers = {
    "Authorization": f"Bearer {VIRTUAL_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json={
        "model": "claude-sonnet-4-5",
        "messages": [{"role": "user", "content": "Count to 10"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line_text = line.decode("utf-8")
        if line_text.startswith("data: "):
            data_str = line_text[6:]  # Remove "data: " prefix
            if data_str == "[DONE]":
                break
            try:
                data = json.loads(data_str)
                if "choices" in data and len(data["choices"]) > 0:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        print(delta["content"], end="", flush=True)
            except json.JSONDecodeError:
                pass
print()  # New line at the end
```

## Example 8: Environment Configuration

```python
import os
from pathlib import Path
from openai import OpenAI

# Load from .env file
def load_env_file(env_path=".env"):
    """Load environment variables from .env file"""
    env_vars = {}
    if Path(env_path).exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value.strip('"\'')
    return env_vars

# Load environment
env = load_env_file()
VIRTUAL_KEY = env.get("VIRTUAL_KEY", os.getenv("VIRTUAL_KEY"))
NGINX_PORT = env.get("NGINX_HTTP_PORT", "3000")
BASE_URL = f"http://localhost:{NGINX_PORT}/api/litellm/v1"

client = OpenAI(
    api_key=VIRTUAL_KEY,
    base_url=BASE_URL
)

# Use client as before
response = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Best Practices

1. **Use Virtual Key**: Always use Virtual Key, never Master Key in client code
2. **Error Handling**: Always handle API errors gracefully
3. **Rate Limiting**: Implement retry logic for rate limit errors
4. **Environment Variables**: Store keys in environment variables, not in code
5. **Connection Timeout**: Set appropriate timeouts for production use

## Related Documentation

- **[API for Agents](../integrations/api-for-agents.md)** - Complete API reference
- **[Configuration Guide](../configuration.md)** - Configuration options
- **[Troubleshooting](../troubleshooting.md)** - Common issues and solutions

