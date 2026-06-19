<div align="center">

# 🌸 Love AI

### Your Private, Self-Hosted AI Gateway

**One API. Every model. Zero data leaks. Runs on your machine.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-Alpha-orange)]()
[![Stars](https://img.shields.io/github/stars/Luv-Goel/Love_AI?style=social)](https://github.com/Luv-Goel/Love_AI/stargazers)

[**Quick Start**](#-quick-start) · [**Features**](#-features) · [**Architecture**](#-architecture) · [**Roadmap**](#-roadmap) · [**Contributing**](#-contributing)

</div>

---

## 🔒 Why Love AI?

Every time you send a prompt to a cloud AI service, your data — your code, your documents, your ideas — travels to someone else's server. **Love AI keeps everything local.**

Love AI is a **privacy-first, self-hosted AI gateway** that runs entirely on your own machine or VPS. It gives you a single unified OpenAI-compatible API endpoint that routes requests across any number of AI providers — local or cloud — without ever phoning home, logging your conversations, or leaking your keys.

Think of it as a personal AI traffic controller that:

- 🔑 Issues **project-scoped virtual API keys** so your real vendor keys never leave your server
- 🌐 Adds **built-in private web search** powered by a self-hosted search index — no Google, no Bing
- 🔀 **Automatically routes** between providers with fallback chains and smart retries
- 🖥️ Ships with a **clean admin dashboard** for managing keys, models, and routing rules
- 🤖 Works out of the box with **Claude Code, Cursor, Continue, any OpenAI-compatible client**

---

## ✨ Features

### 🔑 Virtual Key Management
Issue `sk-loveai-*` keys per project. Your actual vendor API keys (NVIDIA, Anthropic, OpenAI, etc.) stay locked on the server, hashed in a local SQLite database. Revoke or rotate keys instantly from the dashboard without touching your code.

### 🌐 Private Web Search (Love Index)
Every key can optionally enable server-side web search. When a model needs to search the web, Love AI intercepts the tool call and executes it using a **self-hosted YaCy search index** — no third-party search APIs, no tracking. Results are enriched by **Crawl4AI** for full-page content extraction.

The interceptor is **client-aware**: if your client (e.g., a custom MCP harness) already provides its own `web_search` tool, Love AI detects it and steps aside, letting the client execute locally. Zero interference.

### 🔀 Intelligent Model Routing
Powered by [LiteLLM](https://github.com/BerriAI/litellm) under the hood, Love AI supports:
- **100+ providers**: NVIDIA NIM, Anthropic, OpenAI, Azure, Bedrock, VertexAI, Ollama, vLLM, and more
- **Waterfall fallbacks**: configure priority chains (e.g., `llama-70b → llama-8b`)
- **Automatic retries**: up to 3 attempts with exponential backoff
- **Provider jailing**: backends with too many errors are cooled down for 30 minutes

### 🖥️ Admin Dashboard
A built-in web UI lets you:
- Create, list, and delete virtual keys
- View provider and routing configurations
- Monitor total spend across all keys
- Toggle web search per project key

### 🤖 Universal Client Compatibility
Love AI speaks the OpenAI API format. Point any client at `http://localhost:6666/v1` and it just works — Claude Code, Continue, Cursor, LangChain, LlamaIndex, OpenAI SDKs in any language.

```bash
# Claude Code
export ANTHROPIC_BASE_URL=http://localhost:6666
export ANTHROPIC_API_KEY=sk-loveai-yourproject-...

# Python OpenAI SDK
client = OpenAI(base_url="http://localhost:6666/v1", api_key="sk-loveai-yourproject-...")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Clients                            │
│          (Claude Code / Cursor / Continue / Any SDK)            │
└─────────────────────────┬───────────────────────────────────────┘
                          │  OpenAI-compatible API
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Love AI Gateway  :6666                      │
│                                                                 │
│   ┌─────────────────┐     ┌──────────────────────────────────┐  │
│   │  Auth Layer     │     │     SSE Stream Interceptor       │  │
│   │  Virtual Keys   │────▶│  Policy: INTERCEPT / BYPASS      │  │
│   │  SQLite DB      │     │  Client-aware tool detection     │  │
│   └─────────────────┘     └──────────────┬───────────────────┘  │
│                                          │                      │
└──────────────────────────────────────────┼──────────────────────┘
                                           │
                 ┌─────────────────────────┤
                 │                         │
                 ▼                         ▼
┌──────────────────────────┐   ┌───────────────────────────┐
│      Love Smith          │   │     Love Tools            │
│  (LiteLLM Router :6665)  │   │                           │
│                          │   │  ┌──────────────────────┐ │
│  • 100+ providers        │   │  │  Love Index (YaCy)   │ │
│  • Fallback chains       │   │  │  Private web search  │ │
│  • Retries & jailing     │   │  └──────────────────────┘ │
│  • Cost tracking         │   │  ┌──────────────────────┐ │
│                          │   │  │  Love Crawler        │ │
│  Providers:              │   │  │  (Crawl4AI)          │ │
│  NVIDIA NIM, Anthropic,  │   │  │  URL content extract │ │
│  OpenAI, Ollama, vLLM,   │   │  └──────────────────────┘ │
│  Azure, Bedrock, +more   │   └───────────────────────────┘
└──────────────────────────┘
```

### Component Map

| Component | Technology | Role |
|-----------|------------|------|
| **Love AI Gateway** | FastAPI + Python | Auth, routing, SSE interception |
| **Love Smith** | LiteLLM Proxy | Model routing, fallbacks, retries |
| **Love Index** | YaCy | Self-hosted private web search |
| **Love Crawler** | Crawl4AI | Full-page content extraction |
| **Admin UI** | React + Vite | Key and model management dashboard |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for Love Smith + Love Index)
- Node.js 18+ (for building the admin UI)

### 1. Clone the repo

```bash
git clone https://github.com/Luv-Goel/Love_AI.git
cd Love_AI
```

### 2. Configure your providers

Edit `love_engine_config.yaml` to add your AI providers:

```yaml
model_list:
  - model_name: fast          # virtual model name your clients use
    love_engine_params:
      model: openai/meta/llama-3.1-70b-instruct
      api_base: https://integrate.api.nvidia.com/v1
      api_key: os.environ/NVIDIA_API_KEY   # read from env, never hardcoded
```

Set your vendor keys as environment variables:

```bash
export NVIDIA_API_KEY=nvapi-...
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
```

### 3. Start the stack

**Windows (native):**
```powershell
.\start_all.ps1
```

**Docker Compose (full stack):**
```bash
docker-compose up -d
```

### 4. Create your first virtual key

```bash
curl -X POST http://localhost:6666/admin/api/v1/virtual-keys \
  -H "Content-Type: application/json" \
  -d '{"project_name": "my-project", "allowed_models": "*", "enable_web_search": false}'
```

The response includes your `sk-loveai-*` key. Use it in any OpenAI-compatible client.

### 5. Open the admin dashboard

Visit `http://localhost:6666` in your browser.

---

## 🗺️ Roadmap

Love AI is actively being developed. This is the minimum working prototype — a solid foundation that already handles the core gateway, interception, and private search use cases.

### ✅ Done (v0.1 — Current)
- [x] FastAPI reverse proxy with OpenAI-compatible API
- [x] Virtual API key management with SHA-256 hashing
- [x] Per-key `enable_web_search` toggle
- [x] Client-aware SSE stream interceptor (INTERCEPT / BYPASS policy)
- [x] YaCy integration for private web search
- [x] Crawl4AI integration for URL content extraction
- [x] LiteLLM-based model routing with fallback chains
- [x] Admin dashboard (React + Vite)
- [x] Windows-native startup scripts

### 🚧 Coming Soon (v0.2)
- [ ] Live RPM rate limiting enforcement
- [ ] Token-level spend tracking and budget enforcement
- [ ] Non-streaming tool interception path
- [ ] Async SQLite (aiosqlite)
- [ ] Full admin dashboard CRUD for providers and routing rules

### 🔮 Future
- [ ] Semantic caching layer
- [ ] Prompt injection guardrails
- [ ] Multi-user auth with role-based access
- [ ] Prometheus metrics + Grafana dashboard
- [ ] One-click VPS deployment script
- [ ] Browser extension for seamless private search

---

## 🙏 Credits & Inspiration

Love AI stands on the shoulders of incredible open-source projects:

| Project | Role in Love AI |
|---------|------------------|
| [**LiteLLM**](https://github.com/BerriAI/litellm) | The routing engine that powers Love Smith — 100+ provider support, fallbacks, retries |
| [**Crawl4AI**](https://github.com/unclecode/crawl4ai) | The crawler that powers Love Crawler — fast, async, LLM-friendly web extraction |
| [**YaCy**](https://github.com/yacy/yacy_search_server) | The search engine that powers Love Index — fully self-hosted, zero tracking |
| [**FastAPI**](https://github.com/tiangolo/fastapi) | The async web framework powering the gateway |
| [**httpx**](https://github.com/encode/httpx) | Async HTTP client for upstream streaming |

---

## 📁 Project Structure

```
Love_AI/
├── gateway.py               # Main FastAPI app — auth, admin API, proxy entry
├── gateway_interceptor.py   # SSE stream interceptor — INTERCEPT/BYPASS policy
├── agent_tools.py           # Web search + URL extraction tool implementations
├── love_engine_config.yaml  # Model list and router settings (your config file)
├── docker-compose.yml       # Full stack: Love Smith + Love Index + Love Crawler
├── start_all.ps1            # Windows native startup script
├── start.bat                # Windows batch launcher
├── frontend/                # React + Vite admin dashboard
├── love_engine/             # LiteLLM (Love Smith backend)
├── love_crawler/            # Crawl4AI service
└── love_smith/              # Love Smith proxy service wrapper
```

---

## 🤝 Contributing

Contributions are welcome! Love AI is in active early development — this is the best time to get involved.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Built with ❤️ for privacy, freedom, and full control over your AI stack.**

*If Love AI saves you money or protects your data, please consider giving it a ⭐*

</div>
