<div align="center">

# 🌸 Love AI

### Your Personal AI Cloud

**One endpoint. Every model. Infinite resilience. Runs on your machine.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-Alpha-orange)]()
[![Stars](https://img.shields.io/github/stars/Luv-Goel/Love_AI?style=social)](https://github.com/Luv-Goel/Love_AI/stargazers)

[**What is Love AI?**](#-what-is-love-ai) · [**Architecture**](#-architecture) · [**Features**](#-features-in-depth) · [**Virtual Models**](#-the-virtual-model-system) · [**Quick Start**](#-quick-start) · [**Roadmap**](#-roadmap)

</div>

---

## 🌐 What is Love AI?

Love AI is a **self-hosted personal AI cloud** that sits invisibly between your applications and every AI provider you use.

Every AI application you build or run — coding assistants, agent frameworks, chat clients, scripts — connects to a **single local endpoint**. Love AI handles everything else: which provider serves the request, which model responds, what happens when a provider is down, how your API keys are protected, and whether your data ever leaves your machine.

Your applications never change. Your real API keys never leave your server. Provider outages, rate limits, and model failures become invisible.

```
┌───────────────────────────────────────────┐
│            Your Applications              │
│  Claude Code · Cursor · Agents · Scripts  │
└─────────────────────┬─────────────────────┘
                      │ http://localhost:6666/v1
                      │ (standard OpenAI API format)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                        🌸  Love AI                              │
│                   Your Personal AI Cloud                        │
│                                                                 │
│   Auth · Routing · Fallbacks · Keys · Search · Tools · UI      │
│                                                                 │
└──────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
  NVIDIA NIM  Anthropic  OpenAI    Ollama     Groq / Mistral
  Google AI   Cerebras   Azure     vLLM       Bedrock / +more
```

### The Core Problem Love AI Solves

Without Love AI, each project has its own vendor key, its own retry logic, its own model name, and breaks independently when a provider has an outage. With Love AI, every project points at `localhost:6666` and the chaos is absorbed invisibly.

---

## 🏗️ Architecture

Love AI is composed of five specialized subsystems, each with a single clear responsibility:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Love AI Gateway  :6666                           │
│                                                                         │
│  ┌──────────────────────────┐    ┌──────────────────────────────────┐   │
│  │     Love Gate            │    │       Love Watch                 │   │
│  │                          │    │                                  │   │
│  │  • Virtual key auth      │───▶│  • SSE stream interception       │   │
│  │  • Per-project isolation │    │  • INTERCEPT / BYPASS policy     │   │
│  │  • Model allow-listing   │    │  • Client-aware tool detection   │   │
│  │  • Admin control plane   │    │  • Server-side tool execution    │   │
│  │  • Usage accounting      │    │  • Multi-turn agent loops        │   │
│  └──────────────────────────┘    └──────────────────┬───────────────┘   │
└──────────────────────────────────────────────────────┼──────────────────┘
                                                       │
                              ┌────────────────────────┤
                              │                        │
                              ▼                        ▼
     ┌────────────────────────────────┐   ┌────────────────────────────────┐
     │         Love Smith  :6665      │   │         Love Tools             │
     │                                │   │                                │
     │  • Unified provider router     │   │  ┌──────────────────────────┐  │
     │  • 100+ provider adapters      │   │  │      Love Index          │  │
     │  • Waterfall fallback chains   │   │  │  Self-hosted web search  │  │
     │  • Multi-key load balancing    │   │  │  Zero tracking, private  │  │
     │  • Rate limit awareness        │   │  └──────────────────────────┘  │
     │  • Warm model tracking         │   │  ┌──────────────────────────┐  │
     │  • Self-healing jail system    │   │  │      Love Crawler        │  │
     │  • Cost & token accounting     │   │  │  Full-page extraction    │  │
     │  • Live config reload          │   │  │  LLM-optimized output    │  │
     └────────────────────────────────┘   │  └──────────────────────────┘  │
                                          └────────────────────────────────┘
```

### Component Overview

| Subsystem | Role |
|-----------|------|
| **Love Gate** | The front door — virtual key authentication, per-project isolation, admin API, usage accounting |
| **Love Watch** | The interceptor — inspects streaming responses, detects tool calls, executes them server-side, loops agent workflows |
| **Love Smith** | The router — dispatches requests to the right provider, manages fallbacks, keys, rate limits, and provider health |
| **Love Index** | The private search engine — fully self-hosted, no external search APIs, no query tracking |
| **Love Crawler** | The content extractor — fetches and distills full web pages into LLM-digestible text |

---

## ✨ Features In Depth

### 🔑 Virtual Key Management

Every project receives a `sk-loveai-*` virtual key. Real vendor credentials (NVIDIA NIM, Anthropic, OpenAI, Groq, etc.) are stored encrypted on the server and **never exposed to any client**. Each virtual key carries:

- A list of allowed virtual models
- A budget cap (spend limit)
- An RPM quota (rate limit)
- An expiry date
- A web search toggle
- Project-level isolation from all other keys

Rotating a compromised vendor key requires changing it in one place — Love AI — and zero projects break.

### 🔀 Intelligent Model Routing via Love Smith

Love Smith is Love AI's routing core. Inspired by the excellent work of the open-source LLM routing community, it supports:

- **100+ providers** out of the box — NVIDIA NIM, Anthropic, OpenAI, Azure, Bedrock, VertexAI, Groq, Mistral, Cerebras, Google AI Studio, Ollama, vLLM, and more
- **Waterfall fallback chains** — if a model fails, the next in the chain takes over transparently
- **Multi-key rotation** — multiple API keys per provider with round-robin, least-used, weighted, latency-based, or token-based balancing
- **Rate-limit awareness** — understands shared, per-model, group, and IP-based limits per vendor
- **Self-healing jail system** — unhealthy models, keys, and providers are automatically quarantined and retested
- **Warm model preference** — recently successful models receive routing preference to avoid cold starts
- **Model pinning** — successful instances are pinned temporarily to stabilize agent workflows
- **Live config reload** — add providers, rotate keys, change routing without restarting

### 🧠 The Virtual Model System

Clients never reference raw provider model names. Instead, Love AI exposes **virtual models** — stable endpoints that map to one or more real models behind the scenes.

**Vendor-level virtual models** expose quality tiers for each provider:
```
nvidia_high   →  meta/llama-3.1-405b-instruct  (NVIDIA NIM)
nvidia_mid    →  meta/llama-3.1-70b-instruct   (NVIDIA NIM)
nvidia_low    →  meta/llama-3.1-8b-instruct    (NVIDIA NIM)
```

**Global virtual models** route across all providers in a quality-tiered pool:
```
all_high      →  [nvidia_high, anthropic_high, openai_high, ...]  (best available)
all_mid       →  [nvidia_mid,  groq_mid,       mistral_mid,  ...]  (balanced)
all_low       →  [nvidia_low,  groq_low,        gemma_low,   ...]  (fastest/cheapest)
```

**Capability-based virtual models** route by task type:
```
code_best     →  best available coding model across all providers
fast_chat     →  lowest-latency conversational model available
cheap_reason  →  cheapest model with reasoning capability
vision_fast   →  fastest multimodal model
```

When `meta/llama-3.1-405b` gets deprecated or a provider raises prices, you update one line in the config. Every project that uses `nvidia_high` automatically gets the new model with zero code changes.

### 🔀 Waterfall Routing

Virtual models define ordered fallback chains. If the primary model fails, Love AI silently moves to the next:

```yaml
model_name: all_high
love_engine_params:
  model: openai/meta/llama-3.1-405b-instruct
  api_base: https://integrate.api.nvidia.com/v1

fallbacks:
  - all_high-fallback:          # 70b on same provider
  - all_high-fallback-2:        # different provider entirely

routing_strategy: latency-based-routing
```

Your client receives a successful response. The fallback cascade happened invisibly.

### 🔒 Self-Healing Jail System

Love AI automatically isolates failing resources with progressive penalties:

```
First failure    →  jailed for  2 minutes
Second failure   →  jailed for  5 minutes
Third failure    →  jailed for 15 minutes
Fourth failure   →  jailed for 30 minutes
```

Jails exist at three levels — individual model instances, API keys, and entire vendor backends. While jailed, a resource is excluded from all routing. Love AI quietly probes jailed resources and reintroduces them when they recover. No human intervention required.

### 🌐 Private Web Search (Love Index + Love Crawler)

When a model needs to search the web, Love AI intercepts the tool call and executes it using a **fully self-hosted search stack** — no Google, no Bing, no third-party APIs. No search query ever leaves your machine.

**Love Watch** — the SSE stream interceptor — is **client-aware**:
- If your client already provides its own `web_search` tool → Love Watch steps aside and lets the client handle it
- If your client has no web search capability → Love Watch intercepts, executes server-side, and returns the result as if the model had done it natively

The search-then-read workflow:
1. Model calls `web_search(query="...")`
2. Love Watch intercepts the tool call from the stream
3. Love Index returns ranked results from the private search engine
4. Model may call `web_search(url="...")` to read a specific page
5. Love Crawler fetches and distills the full page content
6. Model synthesizes results and continues responding

### 🌊 Universal Streaming

Streaming works identically regardless of provider. Love Watch handles:

- Real-time token streaming
- Tool-call streaming and interception
- Multi-step agent workflows over streamed responses
- Reasoning output streaming
- Structured output streaming

Clients receive streaming behavior matching their expected protocol, regardless of underlying provider differences.

### 🖥️ Admin Control Plane

The built-in admin dashboard provides full operational visibility:

- **Key Management** — create, inspect, revoke, and rotate virtual keys
- **Provider Management** — add, configure, and health-check providers
- **Model Management** — define and update virtual model mappings
- **Usage Analytics** — spend, token usage, and request counts per project
- **Jail Inspection** — view currently jailed models, keys, and providers
- **Routing Visualization** — see which real model served each request

### 🔌 Protocol Invisibility

Love AI speaks the OpenAI wire protocol natively. Every client that works with OpenAI works with Love AI — zero client-side changes required:

```python
# Before Love AI — each project has its own key, breaks on outages
from openai import OpenAI
client = OpenAI(api_key="sk-real-vendor-key-leaking-everywhere")

# After Love AI — one virtual key, all providers, full resilience
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:6666/v1",
    api_key="sk-loveai-myproject-abc123"
)
# identical API surface, works with every provider, keys stay on your server
```

**Supported clients (no modification required):**
- Claude Code — via `ANTHROPIC_BASE_URL`
- Cursor, Continue, and compatible editors
- OpenAI Python / JS / Go / Ruby SDKs
- Anthropic Python / JS SDKs
- Ollama clients via compatible endpoint
- LangChain, LlamaIndex, AutoGen, CrewAI
- Any OpenAI-compatible agent framework

---

## 🗂️ The Virtual Model System

The full virtual model namespace Love AI is designed to expose:

```
Love AI Virtual Model Namespace
│
├── Vendor-Tier Models (per provider)
│   ├── nvidia_high / nvidia_mid / nvidia_low / nvidia_auto
│   ├── anthropic_high / anthropic_mid / anthropic_low
│   ├── groq_high / groq_mid / groq_low
│   ├── google_high / google_mid / google_low
│   └── local_high / local_mid / local_low   (Ollama / vLLM)
│
├── Global Tier Models (cross-provider pools)
│   ├── all_high     →  best available model across all providers
│   ├── all_mid      →  balanced model (speed vs. quality)
│   ├── all_low      →  fastest / cheapest available
│   └── all_auto     →  adaptive selection based on request complexity
│
└── Capability Models (task-routed)
    ├── code_best    →  strongest coding model available
    ├── fast_chat    →  lowest-latency conversational model
    ├── cheap_reason →  cheapest model with reasoning support
    ├── vision_fast  →  fastest model with vision capability
    └── embed_large  →  best embedding model available
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ *(for admin UI development only)*

### 1. Clone

```bash
git clone https://github.com/Luv-Goel/Love_AI.git
cd Love_AI
```

### 2. Configure providers

Edit `love_engine_config.yaml`:

```yaml
model_list:
  - model_name: all_high
    love_engine_params:
      model: openai/meta/llama-3.1-70b-instruct
      api_base: https://integrate.api.nvidia.com/v1
      api_key: os.environ/NVIDIA_API_KEY        # env var — never hardcoded

  - model_name: all_high                        # fallback on same pool
    love_engine_params:
      model: claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: all_low
    love_engine_params:
      model: openai/google/gemma-2-2b-it
      api_base: https://integrate.api.nvidia.com/v1
      api_key: os.environ/NVIDIA_API_KEY

router_settings:
  routing_strategy: latency-based-routing
  cooldown_time: 1800
  allowed_fails: 3
```

Set vendor keys as environment variables — they never go in any config file:

```bash
export NVIDIA_API_KEY=nvapi-...
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GROQ_API_KEY=gsk_...
```

### 3. Start the stack

**Windows:**
```powershell
.\start_all.ps1
```

**Linux / macOS / Docker:**
```bash
docker-compose up -d
```

### 4. Issue your first virtual key

```bash
curl -X POST http://localhost:6666/admin/api/v1/virtual-keys \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-coding-assistant",
    "allowed_models": "*",
    "enable_web_search": true
  }'

# Response:
# { "key": "sk-loveai-my-coding-assistant-a1b2c3d4...", "project": "my-coding-assistant" }
```

### 5. Point your tools at Love AI

```bash
# Claude Code
export ANTHROPIC_BASE_URL=http://localhost:6666
export ANTHROPIC_API_KEY=sk-loveai-my-coding-assistant-a1b2c3d4...

# Python — OpenAI SDK
client = OpenAI(base_url="http://localhost:6666/v1", api_key="sk-loveai-...")

# Any OpenAI-compatible tool
OPENAI_BASE_URL=http://localhost:6666/v1
OPENAI_API_KEY=sk-loveai-...
```

### 6. Open the admin dashboard

`http://localhost:6666`

---

## 📁 Project Structure

```
Love_AI/
├── gateway.py               # Love Gate — auth, admin API, reverse proxy entry
├── gateway_interceptor.py   # Love Watch — SSE stream interceptor, tool execution
├── agent_tools.py           # Web search + page extraction implementations
├── love_engine_config.yaml  # Provider and virtual model configuration
├── docker-compose.yml       # Full stack orchestration
├── start_all.ps1            # Windows native startup
├── start.bat                # Windows batch launcher
│
├── love_smith/              # Love Smith — unified provider router
├── love_engine/             # Routing engine core
├── love_crawler/            # Love Crawler — web content extractor
├── frontend/                # Admin dashboard (React + Vite)
└── ui/                      # UI assets
```

---

## 🗺️ Roadmap

### ✅ v0.1 — Foundation *(current)*

- [x] OpenAI-compatible reverse proxy with full streaming support
- [x] Virtual API key system with SHA-256 hashing
- [x] Per-key model allow-listing and web search toggle
- [x] Client-aware SSE stream interceptor (INTERCEPT / BYPASS policy)
- [x] Private web search via self-hosted search engine (Love Index)
- [x] Web page content extraction via async crawler (Love Crawler)
- [x] Multi-provider routing with fallback chains and provider jailing
- [x] Admin dashboard (React + Vite)
- [x] Docker Compose full-stack deployment
- [x] Windows-native startup scripts

### 🚧 v0.2 — Hardening

- [ ] Live RPM rate limiting enforcement per virtual key
- [ ] Token-level spend tracking and budget enforcement
- [ ] Non-streaming tool interception path
- [ ] Admin authentication (secret-key protected endpoints)
- [ ] Async database layer for concurrent request handling
- [ ] Full admin CRUD for providers, models, and routing rules
- [ ] Provider health dashboard with jail state visualization

### 🔮 v0.3 — Intelligence

- [ ] Capability-aware routing (code / vision / reasoning / embeddings)
- [ ] Warm model tracking and pin-based routing preference
- [ ] Progressive jail penalty system (exponential backoff)
- [ ] Multi-key load balancing with configurable strategy
- [ ] Semantic response caching layer
- [ ] Request complexity estimation for auto-tier routing

### 🌟 v1.0 — Platform

- [ ] Prometheus metrics endpoint + Grafana dashboard
- [ ] Full virtual model namespace (vendor / global / capability tiers)
- [ ] Prompt injection and content policy guardrails
- [ ] One-click VPS deployment script
- [ ] Multi-user auth with role-based access control
- [ ] Live route tracing and request inspector in admin UI
- [ ] Plugin system for custom routing strategies

---

## 🙏 Credits

Love AI would not exist without these outstanding open-source projects that inspired its design and power its internals:

| Project | Contribution to Love AI |
|---------|-------------------------|
| [**LiteLLM**](https://github.com/BerriAI/litellm) | The routing concepts, unified provider interface, and fallback architecture that inspired Love Smith's design |
| [**Crawl4AI**](https://github.com/unclecode/crawl4ai) | The async-first, LLM-optimized crawling approach that Love Crawler is built on |
| [**YaCy**](https://github.com/yacy/yacy_search_server) | The privacy-first, self-hosted search engine powering Love Index |
| [**FastAPI**](https://github.com/tiangolo/fastapi) | The async Python framework the entire gateway layer runs on |
| [**Forge**](https://github.com/deepseek-ai/DeepSeek-Coder) | Agentic workflow patterns that inspired Love Watch's tool interception design |

---

## 🤝 Contributing

Love AI is in active early development — this is the best time to shape its direction. Contributions, issues, and ideas are all welcome.

```bash
git checkout -b feature/my-feature
git commit -m "feat: add my feature"
git push origin feature/my-feature
# open a Pull Request
```

For significant changes, please open an issue first to discuss the approach.

---

## 📄 License

MIT License — see [`LICENSE`](LICENSE) for details.

---

<div align="center">

**Built for developers who believe their prompts, their keys, and their infrastructure should stay theirs.**

*If Love AI saves you money, protects your data, or survives a provider outage for you — please give it a ⭐*

</div>
