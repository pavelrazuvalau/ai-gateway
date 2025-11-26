# JavaScript Examples

<!--
Tags for AI agents:
- javascript
- typescript
- nodejs
- browser
- code-examples
- chat-completions
- streaming
-->

Basic JavaScript and TypeScript examples for integrating with AI Gateway.

> ✅ **Verified:** Examples follow OpenAI-compatible API format and work with AI Gateway.

## Prerequisites

### Node.js

Install required packages:
```bash
npm install openai axios
# or
yarn add openai axios
```

### Browser

Include via CDN:
```html
<!-- For fetch API (native in modern browsers) -->
<!-- No additional libraries needed for basic examples -->
```

## Example 1: Node.js with OpenAI SDK

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.VIRTUAL_KEY || 'sk-your-virtual-key-here',
  baseURL: 'http://localhost:3000/api/litellm/v1', // Replace with your port
});

async function chatCompletion() {
  try {
    const completion = await client.chat.completions.create({
      model: 'claude-sonnet-4-5', // Replace with your model ID
      messages: [
        { role: 'user', content: 'Hello! Explain quantum computing in one sentence.' }
      ],
      temperature: 0.7,
      max_tokens: 200,
    });

    console.log(completion.choices[0].message.content);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

chatCompletion();
```

## Example 2: Streaming Chat Completion (Node.js)

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.VIRTUAL_KEY || 'sk-your-virtual-key-here',
  baseURL: 'http://localhost:3000/api/litellm/v1',
});

async function streamingChat() {
  try {
    const stream = await client.chat.completions.create({
      model: 'claude-sonnet-4-5',
      messages: [
        { role: 'user', content: 'Write a short story about a robot.' }
      ],
      stream: true,
    });

    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || '';
      if (content) {
        process.stdout.write(content);
      }
    }
    console.log(); // New line at the end
  } catch (error) {
    console.error('Error:', error.message);
  }
}

streamingChat();
```

## Example 3: Browser Example (Fetch API)

```html
<!DOCTYPE html>
<html>
<head>
  <title>AI Gateway Example</title>
</head>
<body>
  <div id="output"></div>
  <script>
    async function chatCompletion() {
      const BASE_URL = 'http://localhost:3000/api/litellm/v1';
      const VIRTUAL_KEY = 'sk-your-virtual-key-here'; // In production, get from secure source

      try {
        const response = await fetch(`${BASE_URL}/chat/completions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${VIRTUAL_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'claude-sonnet-4-5',
            messages: [
              { role: 'user', content: 'Hello! Explain quantum computing in one sentence.' }
            ],
            temperature: 0.7,
            max_tokens: 200,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        document.getElementById('output').textContent = data.choices[0].message.content;
      } catch (error) {
        console.error('Error:', error);
        document.getElementById('output').textContent = `Error: ${error.message}`;
      }
    }

    // Call on page load
    chatCompletion();
  </script>
</body>
</html>
```

## Example 4: Browser Streaming (EventSource)

```html
<!DOCTYPE html>
<html>
<head>
  <title>AI Gateway Streaming Example</title>
</head>
<body>
  <div id="output"></div>
  <script>
    async function streamingChat() {
      const BASE_URL = 'http://localhost:3000/api/litellm/v1';
      const VIRTUAL_KEY = 'sk-your-virtual-key-here';

      try {
        const response = await fetch(`${BASE_URL}/chat/completions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${VIRTUAL_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'claude-sonnet-4-5',
            messages: [
              { role: 'user', content: 'Count to 10' }
            ],
            stream: true,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const output = document.getElementById('output');

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6); // Remove "data: " prefix
              if (data === '[DONE]') {
                return;
              }
              try {
                const json = JSON.parse(data);
                const content = json.choices[0]?.delta?.content || '';
                if (content) {
                  output.textContent += content;
                }
              } catch (e) {
                // Ignore JSON parse errors
              }
            }
          }
        }
      } catch (error) {
        console.error('Error:', error);
        document.getElementById('output').textContent = `Error: ${error.message}`;
      }
    }

    streamingChat();
  </script>
</body>
</html>
```

## Example 5: Node.js with Axios

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:3000/api/litellm/v1';
const VIRTUAL_KEY = process.env.VIRTUAL_KEY || 'sk-your-virtual-key-here';

async function chatCompletion() {
  try {
    const response = await axios.post(
      `${BASE_URL}/chat/completions`,
      {
        model: 'claude-sonnet-4-5',
        messages: [
          { role: 'user', content: 'Hello!' }
        ],
        temperature: 0.7,
      },
      {
        headers: {
          'Authorization': `Bearer ${VIRTUAL_KEY}`,
          'Content-Type': 'application/json',
        },
      }
    );

    console.log(response.data.choices[0].message.content);
  } catch (error) {
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else {
      console.error('Error:', error.message);
    }
  }
}

chatCompletion();
```

## Example 6: TypeScript Example

```typescript
import OpenAI from 'openai';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

const client = new OpenAI({
  apiKey: process.env.VIRTUAL_KEY || 'sk-your-virtual-key-here',
  baseURL: 'http://localhost:3000/api/litellm/v1',
});

async function chatCompletion(messages: ChatMessage[]): Promise<string> {
  try {
    const completion = await client.chat.completions.create({
      model: 'claude-sonnet-4-5',
      messages: messages,
      temperature: 0.7,
    });

    return completion.choices[0].message.content || '';
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Chat completion failed: ${error.message}`);
    }
    throw error;
  }
}

// Usage
const messages: ChatMessage[] = [
  { role: 'user', content: 'Hello!' }
];

chatCompletion(messages)
  .then(response => console.log(response))
  .catch(error => console.error(error));
```

## Example 7: Multi-Turn Conversation

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.VIRTUAL_KEY || 'sk-your-virtual-key-here',
  baseURL: 'http://localhost:3000/api/litellm/v1',
});

const messages = [
  { role: 'system', content: 'You are a helpful assistant.' },
  { role: 'user', content: 'What is Python?' }
];

async function conversation() {
  // First turn
  let response = await client.chat.completions.create({
    model: 'claude-sonnet-4-5',
    messages: messages,
  });

  const assistantMessage = response.choices[0].message.content;
  console.log('Assistant:', assistantMessage);
  messages.push({ role: 'assistant', content: assistantMessage });

  // Second turn
  messages.push({ role: 'user', content: 'Can you give me an example?' });
  response = await client.chat.completions.create({
    model: 'claude-sonnet-4-5',
    messages: messages,
  });

  console.log('Assistant:', response.choices[0].message.content);
}

conversation();
```

## Example 8: Error Handling

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.VIRTUAL_KEY || 'sk-your-virtual-key-here',
  baseURL: 'http://localhost:3000/api/litellm/v1',
});

async function chatWithErrorHandling() {
  try {
    const completion = await client.chat.completions.create({
      model: 'claude-sonnet-4-5',
      messages: [{ role: 'user', content: 'Hello!' }],
    });
    console.log(completion.choices[0].message.content);
  } catch (error) {
    if (error instanceof OpenAI.APIError) {
      // Handle API errors
      console.error('API Error:', error.status, error.message);
      if (error.status === 429) {
        console.error('Rate limit exceeded. Please retry later.');
      } else if (error.status === 401) {
        console.error('Authentication failed. Check your Virtual Key.');
      }
    } else {
      console.error('Unexpected error:', error);
    }
  }
}

chatWithErrorHandling();
```

## Example 9: List Available Models

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.VIRTUAL_KEY || 'sk-your-virtual-key-here',
  baseURL: 'http://localhost:3000/api/litellm/v1',
});

async function listModels() {
  try {
    const models = await client.models.list();
    models.data.forEach(model => {
      console.log(`Model ID: ${model.id}, Owner: ${model.owned_by}`);
    });
  } catch (error) {
    console.error('Error:', error.message);
  }
}

listModels();
```

## Best Practices

1. **Environment Variables**: Store Virtual Key in environment variables, never in code
2. **Error Handling**: Always handle errors gracefully
3. **CORS**: For browser applications, configure CORS if needed
4. **Rate Limiting**: Implement retry logic with exponential backoff
5. **Security**: Never expose Master Key in client-side code

## Related Documentation

- **[API for Agents](../integrations/api-for-agents.md)** - Complete API reference
- **[Configuration Guide](../configuration.md)** - Configuration options
- **[Troubleshooting](../troubleshooting.md)** - Common issues and solutions

