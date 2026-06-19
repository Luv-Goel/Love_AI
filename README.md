<div align="center">

# 💜 Love AI

**A self-hosted personal AI cloud — one endpoint, every provider, zero vendor lock-in.**

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](docker-compose.yml)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen.svg)]()

</div>

---

## What is Love AI?

Love AI is a **self-hosted personal AI cloud** that sits transparently between your AI applications and every AI provider you use. Instead of each application talking directly to OpenAI, Anthropic, Groq, Ollama, NVIDIA NIM, Google AI Studio, Cerebras, Mistral, or any other vendor — every application connects only to Love AI.

Love AI becomes your:

- **Universal AI Gateway** — one stable endpoint for all AI access
- **Local AI Cloud** — self-hosted, private, always available
- **Smart Routing Platform** — intelligent, adaptive model selection
- **Failover System** — provider outages become invisible to clients
- **Provider Abstraction Layer** — applications never see vendor specifics
- **Protocol-Compatible AI Hub** — behaves exactly like native providers
- **Self-Healing AI Infrastructure** — monitors, isolates, and recovers from failures automatically

The goal is complete **protocol invisibility**: Claude Code, OpenCode, Hermes, OpenAI SDKs, Anthropic SDKs, Ollama clients, agent frameworks, and coding assistants should all behave exactly as they would against native providers — while Love AI invisibly manages everything behind the scenes.

---

## How It Works

```
┌──────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATIONS                         │
│  Claude Code │ OpenCode │ Hermes │ OpenAI SDK │ Ollama CLI  │
└───────────────────────┬──────────────────────────────────────┘
                        │  Single unified endpoint
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                       LOVE AI                                │
│                                                              │
│  ┌─────────────────────┐  ┌──────────────────────────────┐  │
│  │  gateway.py         │  │  gateway_interceptor.py      │  │
│  │  FastAPI + Admin UI │  │  Protocol translation +      │  │
│  │  Virtual Keys (DB)  │  │  Web search injection        │  │
│  └─────────────────────┘  └──────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  love_engine  (LiteLLM-based routing core)           │    │
│  │  Waterfall fallbacks · Retries · Cooldown jailing    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  love_smith  │  │ love_crawler │  │  frontend / ui   │   │
│  │  Key pools   │  │  Health mon. │  │  Admin dashboard │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└───────────────────────┬──────────────────────────────────────┘
                        │
          ┌─────────────┼──────────────────┐
          ▼             ▼                   ▼
  ┌──────────────┐ ┌──────────┐   ┌──────────────────┐
  │ Cloud        │ │ Local    │   │ Wrapped          │
  │ NVIDIA NIM   │ │ Ollama   │   │ Chatbot proxies  │
  │ Groq         │ │ LM Studio│   │ Internal APIs    │
  │ Google AI    │ └──────────┘   └──────────────────┘
  │ Cerebras     │
  │ Mistral      │
  │ OpenAI-compat│
  └──────────────┘
```

---

## Current Status

> Love AI is in **active development**. The table below shows what is already working versus what is planned. See [ROADMAP.md](ROADMAP.md) for the full timeline.

| Feature | Status |
|---|---|
| FastAPI gateway with virtual key auth (SQLite) | ✅ Working |
| Virtual key creation, listing, deletion | ✅ Working |
| Per-key model restrictions, budget tracking, RPM limits | ✅ Working |
| OpenAI-compatible proxy (`/v1/chat/completions`) | ✅ Working |
| Streaming (SSE) pass-through | ✅ Working |
| LiteLLM-based routing engine (`love_engine`) | ✅ Working |
| Waterfall fallback chains (YAML config) | ✅ Working |
| Automatic retry (up to 3 attempts) | ✅ Working |
| Backend cooldown / jail (30-minute ban on repeated failures) | ✅ Working |
| Web search injection & tool-call interceptor | ✅ Working |
| Admin dashboard (React frontend) | ✅ Working |
| Docker Compose deployment | ✅ Working |
| Windows launcher scripts (`start.bat`, `start_all.ps1`) | ✅ Working |
| Multi-key load balancing with strategies | 🚧 Planned |
| Intelligent routing (latency/warm-model signals) | 🚧 Planned |
| Granular jail levels (model / key / vendor) | 🚧 Planned |
| Warm model preference & model pinning | 🚧 Planned |
| Capability-aware routing | 🚧 Planned |
| Per-project usage analytics dashboard | 🚧 Planned |
| Live config reload without restart | 🚧 Planned |
| Rate-limit pressure awareness | 🚧 Planned |
| Native Anthropic protocol support | 🚧 Planned |
| Ollama protocol endpoint | 🚧 Planned |

---

## Core Concepts

### Virtual Model System

Applications never interact with raw provider model names. Love AI exposes only **virtual models** — stable, named endpoints that internally map to real provider models. If a better model is released or a provider changes pricing, you update the mapping once in `love_engine_config.yaml` and every connected application benefits automatically.

**Vendor-level virtual models** (per provider):

| Virtual Model | Role |
|---|---|
| `{vendor}_high` | Strongest / most capable model from this vendor |
| `{vendor}_mid` | Balanced performance / cost model |
| `{vendor}_low` | Fastest / cheapest model for simple tasks |
| `{vendor}_auto` | Automatically selected by Love AI based on request context |

**Global virtual models** (across all vendors):

| Virtual Model | Role |
|---|---|
| `all_high` | Best model globally across all providers |
| `all_mid` | Balanced model across all providers |
| `all_low` | Fastest / cheapest across all providers |
| `all_auto` | Fully adaptive — Love AI picks based on context |

**Capability-based virtual models** (task-oriented):

| Virtual Model | Role |
|---|---|
| `code_best` | Best model for code generation and analysis |
| `fast_chat` | Optimized for low-latency conversational responses |
| `cheap_reasoning` | Reasoning tasks at lowest cost |
| `vision_fast` | Fast vision / multimodal processing |

These endpoints are stable forever. The real models behind them can change at any time without breaking anything.

---

### Waterfall Routing & Failover

Each virtual model is backed by a **priority-ordered list of real models**. When a request arrives, Love AI attempts them in order and automatically falls back on any failure:

```
Request → Try model_1 (primary)
            ✓ Success → return response
            ✗ Fail    → Try model_2 (fallback)
                          ✓ Success → return response
                          ✗ Fail    → Try model_3 (last resort)
                                        ✓ Success → return response
                                        ✗ All failed → surface error
```

Configured in YAML:
```yaml
router_settings:
  num_retries: 3
  timeout: 60
  allowed_fails: 3
  cooldown_time: 1800   # 30-minute jail on repeated failures

  fallbacks:
    - {"all_high": ["all_high-fallback"]}
```

The client receives a successful response without ever knowing a fallback occurred.

---

### Self-Healing Jail System

When a backend fails repeatedly (`allowed_fails` threshold), Love AI automatically **jails** it for `cooldown_time` seconds, removing it from the routing pool. The system heals itself — jailed backends are automatically retested and re-enabled when the cooldown expires.

Future versions will add granular jail levels (model-level, key-level, vendor-level) with progressive penalty escalation.

---

### Virtual API Keys

Applications connect to Love AI using **virtual keys** — project-scoped credentials that never expose real provider credentials. Each virtual key stores:

- `project_name` — which project this key belongs to
- `allowed_models` — comma-separated list or `*` for all
- `budget` — max spend limit (USD)
- `spend` — current cumulative spend
- `rpm_limit` — requests per minute cap
- `enable_web_search` — whether this key can use the web search injector

Your actual provider API keys never leave Love AI.

---

### Web Search Injection

When `enable_web_search` is enabled on a virtual key, Love AI automatically injects a `web_search` tool into outgoing requests and intercepts the tool-call loop in streaming responses. This makes any model — even those that do not natively browse the web — capable of real-time web search, transparently, without any changes to the client application.

---

### Streaming Support

Love AI provides full streaming support across all provider backends:

- Real-time token streaming (SSE)
- Tool-call streaming with interception support
- Reasoning output streaming
- Streaming works identically whether the backend is NVIDIA NIM, Groq, Ollama, or any OpenAI-compatible service

---

## Repository Structure

```
Love_AI/
├── gateway.py                  # Main FastAPI gateway — virtual keys, admin API, routing dispatch
├── gateway_interceptor.py      # Protocol translation, streaming interceptor, web search injection
├── agent_tools.py              # Tool execution (web search via love_crawler)
├── love_engine/                # LiteLLM-based routing engine (forked/customized)
│   ├── love_engine/            # Core Python package
│   ├── backend/                # Backend management
│   ├── gateway/                # Gateway layer
│   ├── schema.prisma           # Database schema
│   ├── proxy_server_config.yaml
│   ├── model_prices_and_context_window.json
│   ├── provider_endpoints_support.json
│   └── docker-compose.yml
├── love_smith/                 # Key management service (port 6665)
├── love_crawler/               # Web search and health monitoring
├── frontend/                   # React admin dashboard (npm build → dist/)
├── ui/                         # Additional UI components
├── love_engine_config.yaml     # Virtual models + routing rules + provider config
├── docker-compose.yml          # Top-level Docker Compose for the full stack
├── start.bat                   # Windows quick-start (cmd)
├── start_all.ps1               # Windows PowerShell full-stack launcher
├── robust_test.py              # Comprehensive routing and failover test suite
├── robust_test_report.md       # Test results and coverage report
├── test_endpoints.py           # API endpoint smoke tests
├── VISION.md                   # Full project vision document
├── ARCHITECTURE.md             # Detailed architecture reference
├── ROADMAP.md                  # Development roadmap (current vs planned)
└── README.md                   # This file
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (recommended)
- At least one AI provider API key

### Docker (Recommended)

```bash
git clone https://github.com/Luv-Goel/Love_AI.git
cd Love_AI

# Edit love_engine_config.yaml — add your provider keys
# Then start everything:
docker compose up -d
```

### Windows

```bat
git clone https://github.com/Luv-Goel/Love_AI.git
cd Love_AI
start.bat
```

Full stack with PowerShell:

```powershell
./start_all.ps1
```

### Linux / macOS

```bash
git clone https://github.com/Luv-Goel/Love_AI.git
cd Love_AI
pip install -r requirements.txt
python gateway.py
```

The gateway starts on **`http://localhost:8000`** by default. The admin dashboard is available at **`http://localhost:8000/admin`**.

---

## Configuration

Edit `love_engine_config.yaml` to define your providers, models, and virtual model fallback chains:

```yaml
model_list:
  # Primary: NVIDIA NIM — 70B model under "all_high"
  - model_name: all_high
    love_engine_params:
      model: openai/meta/llama-3.1-70b-instruct
      api_base: https://integrate.api.nvidia.com/v1
      api_key: os.environ/NVIDIA_API_KEY

  # Fallback: NVIDIA NIM — 8B model
  - model_name: all_high-fallback
    love_engine_params:
      model: openai/meta/llama-3.1-8b-instruct
      api_base: https://integrate.api.nvidia.com/v1
      api_key: os.environ/NVIDIA_API_KEY

  # Low tier
  - model_name: all_low
    love_engine_params:
      model: openai/google/gemma-2-2b-it
      api_base: https://integrate.api.nvidia.com/v1
      api_key: os.environ/NVIDIA_API_KEY

router_settings:
  num_retries: 3
  timeout: 60
  allowed_fails: 3
  cooldown_time: 1800

  fallbacks:
    - {"all_high": ["all_high-fallback"]}
```

Set your provider keys as environment variables:
```bash
export NVIDIA_API_KEY="nvapi-..."
export GROQ_API_KEY="gsk_..."
export OPENAI_API_KEY="sk-..."
```

---

## Connecting Your Applications

Once Love AI is running, point any OpenAI-compatible client at it. First, create a virtual key via the admin dashboard at `http://localhost:8000/admin` or via API:

```bash
curl -X POST http://localhost:8000/admin/api/v1/virtual-keys \
  -H "Content-Type: application/json" \
  -d '{"project_name": "my-project", "allowed_models": "*"}'
# Returns: {"api_key": "sk-loveai-myproject-..."}
```

Then use that key anywhere:

**Python (OpenAI SDK):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-loveai-myproject-..."   # Your virtual key
)

response = client.chat.completions.create(
    model="all_high",                   # Virtual model
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Environment variable (for Claude Code, OpenCode, Hermes):**
```bash
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="sk-loveai-myproject-..."
# No other changes needed — all tools work as-is
```

**curl:**
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-loveai-myproject-..." \
  -H "Content-Type: application/json" \
  -d '{"model": "all_high", "messages": [{"role": "user", "content": "Hi"}], "stream": true}'
```

---

## Supported Providers

Any provider with an OpenAI-compatible `/v1/chat/completions` endpoint works out of the box:

| Provider | Type | Notes |
|---|---|---|
| NVIDIA NIM | Cloud | Tested; used in default config |
| Groq | Cloud | OpenAI-compatible |
| Google AI Studio | Cloud | OpenAI-compatible (Gemini models) |
| Cerebras | Cloud | OpenAI-compatible |
| Mistral | Cloud | OpenAI-compatible |
| OpenAI | Cloud | Direct or via Azure |
| Ollama | Local | OpenAI-compatible on port 11434 |
| LM Studio | Local | OpenAI-compatible |
| Any OpenAI-compat service | Any | Set `api_base` in config |

---

## Design Principles

**Protocol Invisibility** — Clients must not detect Love AI. Applications behave identically to their native provider behavior.

**Stability first** — Hiding backend instability is more valuable than squeezing marginal latency gains. A reliable 200 ms response beats an unreliable 150 ms one.

**Resource efficiency** — Love AI runs continuously on a development laptop without becoming a burden. No heavy daemons, no unnecessary memory pressure.

**Extensibility** — New providers, new virtual models, and new routing strategies are YAML entries and small code additions — not architectural changes.

**Local-first security** — Provider credentials never leave the local machine. All isolation happens inside Love AI before traffic reaches the internet.

---

## Future Vision

Love AI is being developed toward:

- A **local OpenRouter alternative** — every feature of a managed AI routing service, running entirely on your own machine
- A **universal AI operating layer** — the single integration point for all personal and development AI workflows
- A **self-healing AI infrastructure platform** — monitors, adapts, and recovers without manual intervention
- A **centralized AI service hub** — coding assistants, research agents, and automation pipelines all connect to one endpoint

See [ROADMAP.md](ROADMAP.md) for the detailed plan.

---

## Docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — Detailed component architecture, data flows, and subsystem descriptions
- [ROADMAP.md](ROADMAP.md) — Current vs planned features with phase timeline
- [VISION.md](VISION.md) — Full long-term product vision

---

## Contributing

Contributions are welcome. Open an issue before submitting a large PR to discuss the approach. For bug reports, include the relevant section of `love_engine_config.yaml` (with keys redacted) and the request/response pair that triggered the issue.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
Made with 💜 by <a href="https://github.com/Luv-Goel">Luv Goel</a>
</div>
