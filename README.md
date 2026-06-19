<div align="center">

# 🌸 Love AI
### Your Personal, Self-Healing AI Cloud

**One endpoint. Every model. Infinite resilience. Runs entirely on your machine.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-Alpha-orange)]()

[**Philosophy**](#-the-philosophy-of-love-ai) · [**Core Features**](#-core-features--capabilities) · [**Architecture**](#-architecture--subsystems) · [**Virtual Models**](#-the-virtual-model-system) · [**Roadmap**](#-future-roadmap) · [**Quick Start**](#-quick-start)

---

</div>

## 🌐 The Philosophy of Love AI

**Stop hardcoding provider APIs.** 

Love AI is a **self-hosted personal AI cloud** designed to sit invisibly between your applications and every AI provider on the planet. Instead of every app (like Cursor, Claude Code, Agent frameworks, or scripts) talking directly to OpenAI, Anthropic, Ollama, Groq, or NVIDIA NIM, **all applications connect only to Love AI.**

Love AI becomes your local AI operating layer—a universal gateway, smart router, failover system, and protocol abstraction layer. Applications feel as though they are talking directly to the original provider, while Love AI invisibly handles rate limits, provider outages, key rotation, and model fallbacks behind the scenes.

**Your applications never change. Your real API keys never leave your server.**

---

## 🏗️ Architecture & Subsystems

Love AI operates as a symphony of microservices working seamlessly to abstract the complexity of the AI ecosystem.

```mermaid
graph TD
    A[Your Apps <br/> Cursor, Agents, Scripts] -->|Native OpenAI / Anthropic / Ollama Protocols| B(Love Gate)
    
    subgraph 🌸 Love AI Core
    B[Love Gate <br/> Auth & Proxy] --> C[Love Watch <br/> Interceptor & Tools]
    C --> D[Love Smith <br/> Intelligent Router]
    D --> E[Love Engine <br/> Protocol Translator]
    end
    
    subgraph Downstream Providers
    D -.->|Waterfall Fallback| P1((OpenAI))
    D -.->|Waterfall Fallback| P2((Anthropic))
    D -.->|Waterfall Fallback| P3((Groq / Mistral))
    D -.->|Waterfall Fallback| P4((Local Ollama))
    end
    
    subgraph Upcoming Services
    B -.-> F(Love Crawler <br/> Web Extraction)
    B -.-> G(Love Index <br/> Private Search)
    end
```

| Subsystem | Role | Status |
|-----------|------|--------|
| **Love Gate** | The Front Door. Handles virtual key authentication, API quota tracking, and multi-protocol proxying. | ✅ Live |
| **Love Watch** | The Interceptor. Inspects streams in real-time, injects context, and handles server-side tool execution. | ✅ Live |
| **Love Smith** | The Router. Makes intelligent dispatch decisions based on latency, model warmth, jail status, and capabilities. | ✅ Live |
| **Love Engine** | The Translator. Converts universal prompts into provider-specific schemas (e.g. Bedrock, Vertex, Anthropic). | ✅ Live |
| **Love Crawler** | Content Extractor. Distills web pages into clean LLM-digestible text. | 🚧 Alpha / Upcoming |
| **Love Index** | Private Search Engine. Fully self-hosted web search without reliance on external search APIs. | 🚧 Alpha / Upcoming |

---

## ✨ Core Features & Capabilities

Love AI is built for absolute stability and performance. Here's how it achieves it:

### 🔌 True Multi-Protocol Proxying
Applications can use whatever protocol they want. Love AI intercepts and dynamically maps them to the right backend. We natively support:
- `POST /v1/chat/completions` (OpenAI format)
- `POST /v1/messages` (Anthropic format)
- `POST /api/generate` (Ollama format)
- `POST /chat/completions` & `/responses` (Generic fallbacks)

### 🌊 Waterfall Routing & Fallbacks
Never see a "503 Service Unavailable" again. If `meta/llama-3.1-405b` fails via NVIDIA NIM, Love AI silently catches the error and drops down to `meta/llama-3.1-70b` on Groq, or shifts to a local Ollama model. This creates **automatic resilience** without requiring any user intervention or application retries.

### 🛡️ The Self-Healing Jail System
Love AI constantly monitors provider health. When a model, API key, or entire vendor fails repeatedly, they are sent to "Jail" (temporarily removed from routing pools). 
- **Progressive Penalties:** Each subsequent failure increases the freeze duration.
- **Automatic Recovery:** Love AI probes jailed resources quietly in the background and reintroduces them seamlessly once they recover.

### 🧠 The Virtual Model System
Never hardcode `gpt-4o` or `claude-3-5-sonnet-20240620` in your code again. Instead, use **stable virtual models** that route to the best available real models:
- `all_high`: Bleeding-edge reasoning (GPT-4o, Sonnet 3.5, Llama 405b).
- `all_mid`: Balanced cost and performance (Llama 70b, Haiku).
- `all_low`: Blistering fast and cheap (Llama 8b, Gemma).
- `code_best`: The absolute best model currently available for coding tasks.

### 🔀 Multi-Key Load Balancing
Have multiple tier-free API keys for the same provider? Love AI pools them together, automatically rotating them based on Round Robin, Weighted Distribution, or Rate-Limit pressure to ensure you never exhaust a single key.

### 🔥 Warm Model Pinning
When a local or cloud model responds successfully, Love AI "pins" it as warm. Subsequent requests preferentially reuse this warm model to eliminate cold-start delays, drastically speeding up multi-turn agent workflows.

### 🔑 Secure Virtual Keys
Your real keys stay in your `.env`. You generate `sk-loveai-*` virtual keys for your applications. Each virtual key can be heavily customized:
- Restrict to specific virtual models.
- Set hard spend budgets ($).
- Set Requests Per Minute (RPM) quotas.
- Toggle Web Search capabilities.

---

## 🛣️ Future Roadmap

Love AI is designed to evolve into the ultimate personal AI operating layer. Here is what is on the horizon:

- [ ] **Love Crawler & Love Index Integration**: Fully operationalizing the local search and web scraping subsystems to give AI models real-time, private internet access.
- [ ] **Capability-Aware Routing**: Automatically routing requests based on payload contents (e.g., if an image is attached, route only to Vision-capable models; if a massive prompt is sent, route to 128k+ context models).
- [ ] **Advanced Usage Analytics Dashboard**: Real-time graphing of token spend, latency distribution, and jail statistics in the Admin UI.
- [ ] **Semantic Caching**: Skipping LLM calls entirely for similar prompts by implementing a fast vector-based cache layer.
- [ ] **Local OpenRouter Alternative**: Opening up the platform for LAN access, allowing your whole team or household to share a unified AI pool.

---

## 🚀 Quick Start

### 1. Configure Your Keys
Add your actual vendor API keys to your environment variables (e.g., `NVIDIA_API_KEY`, `ANTHROPIC_API_KEY`) or inside `love_engine_config.yaml`.

### 2. Boot the System
Run the provided PowerShell script to launch all subsystems on their local ports:
```powershell
.\start_all.ps1
```

### 3. Generate a Virtual Key
Navigate to `http://127.0.0.1:6666/admin/index.html` (Love Gate Dashboard) to generate your first project key (e.g. `sk-loveai-test-123`).

### 4. Connect Your Apps
Point any AI application, coding assistant, or framework at Love AI.

**Example (OpenAI SDK):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:6666/v1",
    api_key="sk-loveai-test-123"
)
```

**Example (Anthropic SDK):**
```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:6666",
    api_key="sk-loveai-test-123"
)
```

**Example (Ollama Client):**
```bash
curl -X POST http://127.0.0.1:6666/api/generate \
  -H "Authorization: Bearer sk-loveai-test-123" \
  -H "Content-Type: application/json" \
  -d '{"model": "all_low", "prompt": "Why is the sky blue?"}'
```

---
*Created with ❤️ for builders who want to control their own AI infrastructure.*
