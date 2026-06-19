# Love AI — Architecture Reference

This document describes the internal architecture of Love AI: its components, data flows, subsystem responsibilities, and design decisions.

---

## High-Level Architecture

Love AI is composed of four primary layers:

```
┌────────────────────────────────────────────────────────┐
│  PROTOCOL LAYER                                           │
│  gateway.py + gateway_interceptor.py                      │
│  OpenAI-compatible API · Virtual key auth · Streaming     │
└───────────────────────────┬──────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────┐
│  ROUTING LAYER                                            │
│  love_engine (LiteLLM-based)                              │
│  Virtual models · Waterfall fallbacks · Retries · Jail    │
└───────────────────────────┬──────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────┐
│  MANAGEMENT LAYER                                         │
│  love_smith (key management) · love_crawler (health)      │
│  SQLite DB · Rate limits · Budget tracking                │
└───────────────────────────┬──────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────┐
│  PROVIDER LAYER                                           │
│  Cloud APIs · Local Ollama · Wrapped services             │
└──────────────────────────────────────────────────────┘
```

---

## Components

### `gateway.py` — Protocol & Auth Gateway

**Role:** Entry point for all client requests. Implements the OpenAI-compatible REST API surface.

**Responsibilities:**
- Expose `/v1/chat/completions`, `/v1/models`, and `/v1/embeddings` endpoints
- Authenticate incoming requests via virtual keys (SQLite DB lookup)
- Enforce per-key model restrictions and rate limits (RPM)
- Track per-key cumulative spend and enforce budget caps
- Delegate routed requests to `love_engine` and proxy responses back
- Serve the admin API (`/admin/api/v1/...`) for virtual key CRUD
- Serve the compiled React admin dashboard from `frontend/dist/`

**Key design decisions:**
- Built on FastAPI with async request handling
- Virtual keys stored in SQLite with schema managed by the gateway directly
- Spend tracking happens synchronously in the request path (cheap operation for local deployment)

---

### `gateway_interceptor.py` — Protocol Translator & Streaming Interceptor

**Role:** Sits between the gateway and the routing engine. Transforms requests, intercepts streaming tool-call loops, and injects web search capabilities.

**Responsibilities:**
- Translate inbound request formats to `love_engine`'s internal format
- Inject the `web_search` tool definition into requests when `enable_web_search` is active on the virtual key
- Intercept outgoing streaming SSE responses to detect and handle `tool_use` events
- Execute tool calls via `agent_tools.py` and resume the conversation loop
- Reconstruct and re-stream the final response back to the client seamlessly

**Key design decisions:**
- Tool call interception happens at the streaming layer so clients receive clean responses without seeing raw tool invocation messages
- The interceptor is stateless per-request; it does not maintain session state between calls

---

### `agent_tools.py` — Tool Executor

**Role:** Implements tool execution for the interceptor.

**Responsibilities:**
- Handle `web_search` tool calls by dispatching to `love_crawler`
- Format tool results as proper AI conversation messages for re-injection
- Designed to be extended with new tools (code execution, file access, etc.)

---

### `love_engine/` — Routing Engine

**Role:** Core routing, failover, and model management layer. Based on a customized fork of LiteLLM with extensions for Love AI's virtual model system.

**Subsystems:**

#### Virtual Model Router
- Maps incoming model names (e.g., `all_high`) to ordered lists of real backend models
- Executes waterfall fallback on failure: tries each model in priority order
- Retry logic: up to 3 attempts per model before moving to the next

#### Jail / Cooldown System
- Tracks per-backend failure counts
- When `allowed_fails` threshold is crossed: marks backend as **jailed** for `cooldown_time` seconds (default: 1800s / 30 minutes)
- Jailed backends are excluded from the routing pool automatically
- Self-heals: after cooldown expires, the backend re-enters the pool on next request

#### Configuration (`love_engine_config.yaml`)
- `model_list`: defines all real backend models and their credentials
- `router_settings`: global retry, timeout, jail parameters, and fallback chains
- Supports `os.environ/VAR_NAME` syntax for secrets — never hard-coded in config

#### Backend Adapters
- Wraps any OpenAI-compatible HTTP API
- Handles authentication headers, base URL construction, and provider-specific quirks
- Streaming and non-streaming modes both supported

---

### `love_smith/` — Key Management Service

**Role:** Manages the lifecycle of provider API keys and multi-key pool logic.

**Responsibilities (current):**
- Manages provider key storage
- Acts as intermediary for key selection when multiple keys exist for a provider

**Planned extensions:**
- Round-robin, least-used, weighted, and latency-based key rotation strategies
- Per-key RPM and TPM tracking for granular rate-limit pressure management
- Key-level jailing (bad key → removed from pool without affecting the provider)

---

### `love_crawler/` — Web Search & Health Monitor

**Role:** Provides web search capability and future health monitoring for providers.

**Current responsibilities:**
- Execute web searches on behalf of `agent_tools.py`
- Return structured search results for injection into AI conversations

**Planned extensions:**
- Passive health monitoring: periodic pings to detect provider degradation before failures hit
- Latency sampling: maintain rolling latency estimates per backend for intelligent routing
- Warm model detection: signal to the router which backends are actively serving requests

---

### `frontend/` — React Admin Dashboard

**Role:** Web-based control plane for Love AI.

**Current capabilities:**
- Virtual key management (create, list, delete)
- Model listing
- Usage statistics per key
- Basic routing overview

**Planned additions:**
- Real-time request log viewer
- Jail state visualization
- Per-backend health and latency dashboards
- Warm model and routing trace display
- Live configuration editor

Build: `npm install && npm run build` → output to `dist/`, served by `gateway.py` at `/admin`

---

### `ui/` — Additional UI Components

Supplementary UI elements and prototypes for dashboard features not yet integrated into the main frontend build.

---

## Data Flow

### Standard Chat Completions Request

```
Client (SDK / CLI)
  │
  │  POST /v1/chat/completions
  │  Authorization: Bearer sk-loveai-...
  │
  ▼
gateway.py
  │  1. Parse Authorization header
  │  2. Lookup virtual key in SQLite
  │  3. Check: is model in allowed_models? is budget OK? is RPM OK?
  │  4. If web_search enabled → pass to gateway_interceptor
  │     Else → pass directly to love_engine
  │
  ▼
gateway_interceptor.py (if web_search active)
  │  1. Inject web_search tool definition into request
  │  2. Forward to love_engine
  │  3. Stream back response, watching for tool_call events
  │  4. On tool_call: execute via agent_tools.py, inject result, resume
  │
  ▼
love_engine (LiteLLM router)
  │  1. Resolve virtual model name → ordered backend list
  │  2. Pick first non-jailed backend
  │  3. Build provider-specific request (headers, base URL)
  │  4. Attempt request; on failure → retry / next backend
  │  5. Track failure count → jail if threshold exceeded
  │  6. Stream or return response
  │
  ▼
Provider API (NVIDIA NIM / Groq / Ollama / etc.)
  │
  └→ Response streams back through the same chain to the client
```

### Virtual Key Creation

```
Admin UI / API Client
  │
  │  POST /admin/api/v1/virtual-keys
  │  {"project_name": "my-app", "allowed_models": "all_high,all_low", "budget": 10.0}
  │
  ▼
gateway.py (admin route)
  │  1. Generate key: "sk-loveai-{project}-{uuid}"
  │  2. INSERT into SQLite virtual_keys table
  │  3. Return key to caller (shown only once)
  │
  └→ Key stored: project_name, allowed_models, budget, spend=0, rpm_limit, enable_web_search
```

---

## Database Schema

Love AI uses **SQLite** for local persistence — no external database required.

### `virtual_keys` table

| Column | Type | Description |
|---|---|---|
| `api_key` | TEXT PK | The `sk-loveai-...` virtual key string |
| `project_name` | TEXT | Human-readable project label |
| `allowed_models` | TEXT | Comma-separated model names, or `*` for all |
| `budget` | REAL | Maximum spend in USD (`0` = unlimited) |
| `spend` | REAL | Cumulative spend tracked to date |
| `rpm_limit` | INTEGER | Max requests per minute (`0` = unlimited) |
| `enable_web_search` | INTEGER | `1` if web search injection is active |
| `created_at` | TEXT | ISO timestamp of key creation |

---

## Configuration Reference

### `love_engine_config.yaml`

```yaml
model_list:
  - model_name: <virtual_model_name>       # e.g. "all_high"
    love_engine_params:
      model: <provider/model_id>           # e.g. "openai/meta/llama-3.1-70b-instruct"
      api_base: <provider_url>             # e.g. "https://integrate.api.nvidia.com/v1"
      api_key: os.environ/ENV_VAR_NAME     # never hard-code keys

router_settings:
  num_retries: 3              # Attempts per backend before moving to fallback
  timeout: 60                 # Seconds before a request times out
  allowed_fails: 3            # Consecutive failures before jailing a backend
  cooldown_time: 1800         # Seconds a jailed backend stays out of the pool

  fallbacks:
    - {"<virtual_model>": ["<fallback_virtual_model>"]}
```

The key naming convention for fallbacks follows `<model_name>-fallback` by convention (e.g., `all_high` falls back to `all_high-fallback`), but any model name in `model_list` can be a fallback target.

---

## Security Model

Love AI's security design is **local-first**, aimed at practical protection for a self-hosted development environment rather than enterprise compliance.

| Concern | Mitigation |
|---|---|
| Provider API key exposure | Keys stored as environment variables; never in config files or logs |
| Unauthorized gateway access | Virtual key auth on all `/v1/` endpoints |
| Cross-project credential leakage | Per-key `allowed_models` restrictions; keys are opaque to callers |
| Overspending | Per-key `budget` caps tracked per request |
| Rate limit abuse | Per-key `rpm_limit` enforcement |
| Malformed config updates | YAML validation before config activation (planned: live reload with validation) |

The admin API at `/admin/api/v1/` is **not currently authenticated** — it is designed for local use only. Do not expose the gateway to untrusted networks without adding admin route authentication.

---

## Deployment Topology

### Single-Machine (Standard)

All components run on one machine — the gateway, routing engine, key manager, and crawler all communicate over localhost. This is the primary deployment model.

```
localhost:8000  — gateway (client-facing)
localhost:8001  — love_engine internal port
localhost:6665  — love_smith key manager
localhost:XXXX  — love_crawler
```

### Docker Compose

The included `docker-compose.yml` orchestrates the full stack as isolated containers with a shared internal network. Each service is independently restartable. The `love_engine` component has its own `Dockerfile` for isolated builds.

### Windows

Both `start.bat` (cmd) and `start_all.ps1` (PowerShell) are provided for Windows-native development without Docker.

---

## Extension Points

Love AI is designed to be extended at well-defined seams:

| Extension Type | How to Add |
|---|---|
| **New provider** | Add entry to `model_list` in `love_engine_config.yaml` |
| **New virtual model** | Add entries with `model_name: your_virtual_model` in config |
| **New fallback chain** | Add to `router_settings.fallbacks` in config |
| **New routing strategy** | Extend the router in `love_engine/` |
| **New tool** | Add handler in `agent_tools.py`, register in `gateway_interceptor.py` |
| **New admin API route** | Add to `gateway.py` admin router section |
| **New dashboard feature** | Extend `frontend/` React app, rebuild to `dist/` |
