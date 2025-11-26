# Integration Examples

<!--
Tags for AI agents:
- integration
- langchain
- llamaindex
- openai-sdk
- frameworks
- code-examples
-->

Examples of integrating AI Gateway with popular frameworks and tools.

## LangChain Integration

### Basic Example

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Configure LangChain to use AI Gateway
llm = ChatOpenAI(
    model="claude-sonnet-4-5",
    openai_api_key="sk-your-virtual-key-here",
    openai_api_base="http://localhost:3000/api/litellm/v1",
    temperature=0.7,
)

# Use LangChain
messages = [HumanMessage(content="Hello! Explain quantum computing.")]
response = llm.invoke(messages)
print(response.content)
```

### Streaming Example

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

llm = ChatOpenAI(
    model="claude-sonnet-4-5",
    openai_api_key="sk-your-virtual-key-here",
    openai_api_base="http://localhost:3000/api/litellm/v1",
    streaming=True,
)

messages = [HumanMessage(content="Write a short story.")]
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
print()
```

### Chain Example

```python
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(
    model="claude-sonnet-4-5",
    openai_api_key="sk-your-virtual-key-here",
    openai_api_base="http://localhost:3000/api/litellm/v1",
)

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple terms."
)

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("quantum computing")
print(result)
```

## LlamaIndex Integration

### Basic Example

```python
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Configure LlamaIndex to use AI Gateway
llm = OpenAI(
    model="claude-sonnet-4-5",
    api_key="sk-your-virtual-key-here",
    api_base="http://localhost:3000/api/litellm/v1",
    temperature=0.7,
)

# Load documents
documents = SimpleDirectoryReader("data").load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine(llm=llm)
response = query_engine.query("What is the main topic?")
print(response)
```

### Streaming Example

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(
    model="claude-sonnet-4-5",
    api_key="sk-your-virtual-key-here",
    api_base="http://localhost:3000/api/litellm/v1",
    streaming=True,
)

response = llm.stream_complete("Write a story about a robot.")
for token in response:
    print(token.delta, end="", flush=True)
print()
```

## OpenAI SDK (Direct Usage)

The OpenAI SDK works directly with AI Gateway since it's OpenAI-compatible:

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-virtual-key-here",
    base_url="http://localhost:3000/api/litellm/v1"
)

# Use exactly as you would with OpenAI
response = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Custom Application Example

### Simple Chat Application

```python
from openai import OpenAI
import os

class AIGatewayClient:
    def __init__(self, virtual_key=None, base_url=None):
        self.client = OpenAI(
            api_key=virtual_key or os.getenv("VIRTUAL_KEY"),
            base_url=base_url or os.getenv("BASE_URL", "http://localhost:3000/api/litellm/v1")
        )
        self.model = os.getenv("MODEL", "claude-sonnet-4-5")
        self.conversation_history = []

    def chat(self, user_message, system_message=None):
        """Send a message and get response"""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            return f"Error: {str(e)}"

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []

# Usage
client = AIGatewayClient()
response = client.chat("Hello! What is Python?")
print(response)

response = client.chat("Can you give me an example?")
print(response)
```

## FastAPI Integration Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# Initialize AI Gateway client
client = OpenAI(
    api_key=os.getenv("VIRTUAL_KEY"),
    base_url=os.getenv("BASE_URL", "http://localhost:3000/api/litellm/v1")
)

class ChatRequest(BaseModel):
    message: str
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
            temperature=request.temperature,
        )
        return ChatResponse(response=completion.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn main:app --reload
```

## Flask Integration Example

```python
from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("VIRTUAL_KEY"),
    base_url=os.getenv("BASE_URL", "http://localhost:3000/api/litellm/v1")
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    model = data.get("model", "claude-sonnet-4-5")
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
        )
        return jsonify({"response": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run with: flask run
```

## React Integration Example

```javascript
// React component example
import React, { useState } from 'react';

function ChatComponent() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const BASE_URL = 'http://localhost:3000/api/litellm/v1';
  const VIRTUAL_KEY = process.env.REACT_APP_VIRTUAL_KEY;

  const sendMessage = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${VIRTUAL_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-5',
          messages: [{ role: 'user', content: message }],
        }),
      });

      const data = await res.json();
      setResponse(data.choices[0].message.content);
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
      />
      <button onClick={sendMessage} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>
      {response && <div>{response}</div>}
    </div>
  );
}

export default ChatComponent;
```

## Next.js Integration Example

```typescript
// pages/api/chat.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.VIRTUAL_KEY,
  baseURL: process.env.BASE_URL || 'http://localhost:3000/api/litellm/v1',
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const completion = await client.chat.completions.create({
      model: 'claude-sonnet-4-5',
      messages: [{ role: 'user', content: req.body.message }],
    });

    res.status(200).json({ response: completion.choices[0].message.content });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get response' });
  }
}
```

## Related Documentation

- **[Python Examples](python-basic.md)** - Basic Python examples
- **[JavaScript Examples](javascript-basic.md)** - Basic JavaScript examples
- **[API for Agents](../integrations/api-for-agents.md)** - Complete API reference
- **[Configuration Guide](../configuration.md)** - Configuration options

