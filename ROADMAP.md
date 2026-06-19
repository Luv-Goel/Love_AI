# Love AI — Roadmap

This document separates what Love AI **does today** from what is **planned**, organized into development phases.

---

## Current State (v0.x — Active Development)

The following features are **implemented and working** as of the current codebase.

### Core Gateway
- [x] FastAPI gateway (`gateway.py`) with async request handling
- [x] OpenAI-compatible `/v1/chat/completions` endpoint
- [x] `/v1/models` endpoint (returns configured virtual models)
- [x] Streaming support (SSE pass-through)
- [x] Virtual key authentication (SQLite-backed)
- [x] Per-key `allowed_models` enforcement
- [x] Per-key `budget` tracking and enforcement
- [x] Per-key `rpm_limit` rate limiting
- [x] Per-key `enable_web_search` flag

### Routing Engine (`love_engine`)
- [x] LiteLLM-based routing core
- [x] Virtual model name resolution from YAML config
- [x] Waterfall fallback chains (priority-ordered backend lists)
- [x] Automatic retry (up to `num_retries` per backend)
- [x] Backend cooldown / jail: backends are excluded for `cooldown_time` seconds after `allowed_fails` failures
- [x] Self-healing: jailed backends re-enter the pool automatically when cooldown expires
- [x] Any OpenAI-compatible provider as a backend
- [x] Environment variable injection for API keys

### Web Search Injection
- [x] `gateway_interceptor.py` — streaming tool-call interceptor
- [x] Web search tool injection into requests
- [x] Tool-call loop handling: executes search, injects result, resumes conversation
- [x] `love_crawler/` — web search backend

### Key Management (`love_smith`)
- [x] Provider key storage
- [x] Basic key selection

### Admin Dashboard (`frontend/`)
- [x] React admin UI served by gateway at `/admin`
- [x] Virtual key creation, listing, deletion
- [x] Model listing
- [x] Basic usage stats per key

### Infrastructure
- [x] Docker Compose for full stack deployment
- [x] Standalone `Dockerfile` for `love_engine`
- [x] Windows launch scripts (`start.bat`, `start_all.ps1`)
- [x] CI/CD configuration (`love_engine/ci_cd/`)
- [x] Code quality tooling (flake8, basedpyright, semgrep, git hooks)
- [x] Test suite (`robust_test.py`, `test_endpoints.py`)

---

## Phase 1 — Intelligent Routing & Key Management

*Goal: Upgrade from static waterfall routing to adaptive, signal-driven routing.*

### Multi-Key Load Balancing
- [ ] Multiple API keys per provider in `love_smith`
- [ ] Round-robin key rotation
- [ ] Least-used key selection
- [ ] Weighted key distribution
- [ ] Per-key RPM and TPM tracking
- [ ] Key-level jailing (bad key isolated without affecting the provider)
- [ ] Automatic failover within the same provider across keys

### Rate-Limit Pressure Awareness
- [ ] Track requests-per-minute per key vs. provider limit
- [ ] Detect when a key is approaching its rate limit
- [ ] Route around pressure: prefer keys with headroom
- [ ] Differentiated handling for: shared limits, per-model limits, group limits, IP-based limits
- [ ] Backpressure signaling to the router

### Latency-Based Routing Signals
- [ ] Rolling average latency tracking per backend
- [ ] Inject latency signal into routing weight calculations
- [ ] Penalize consistently slow backends before they fail

---

## Phase 2 — Warm Models & Pinning

*Goal: Reduce cold-start latency and stabilize long-running agent workflows.*

### Warm Model Detection
- [ ] Track recency of successful responses per backend
- [ ] Mark backends as **warm** when recently successful
- [ ] Give warm backends a routing preference boost
- [ ] Decay warmth over time (configurable TTL)

### Model Pinning
- [ ] When a backend responds successfully, **pin** it for a configurable duration
- [ ] Future requests to the same virtual model preferentially hit the pinned backend
- [ ] Reduces cold starts in agent chains where context window state matters
- [ ] Pin expires automatically; normal routing resumes
- [ ] Warm status can persist beyond pin expiry

### Cold-Start Reduction
- [ ] love_crawler: active backend pinging to keep warm models loaded
- [ ] Pre-warm requests on gateway startup (optional)
- [ ] Dashboard visibility: show warm/cold status per backend

---

## Phase 3 — Advanced Jail System

*Goal: More granular, graduated failure isolation across all resource levels.*

### Granular Jail Levels
- [ ] **Model-level jail** — specific model at a provider is jailed, other models from the same provider continue routing normally
- [ ] **Key-level jail** — a specific API key is jailed, other keys for the same provider continue
- [ ] **Vendor-level jail** — entire provider is jailed when all keys/models are failing

### Progressive Penalty Escalation
- [ ] First offense: short cooldown (e.g., 5 min)
- [ ] Second offense: medium cooldown (e.g., 15 min)
- [ ] Third offense: long cooldown (e.g., 1 hour)
- [ ] Fourth+ offense: extended cooldown (up to configurable max)
- [ ] Offense counter resets after a configurable clean-period without failures

### Automatic Recovery Testing
- [ ] After cooldown, send a lightweight health probe instead of live traffic
- [ ] Only reintroduce backend on successful health probe
- [ ] Failed health probe → re-jails with escalated penalty

---

## Phase 4 — Capability-Aware Routing

*Goal: Route based on what the request needs, not just model priority.*

### Model Capability Registry
- [ ] Define capabilities per model in config: `chat`, `coding`, `reasoning`, `vision`, `embeddings`, `multimodal`, `tool_use`, `structured_output`, `json_output`, `long_context`
- [ ] Validate incoming requests against capabilities before attempting routing
- [ ] Skip incapable backends silently in the fallback chain

### Task-Specific Virtual Models
- [ ] `code_best` → routes to models with `coding` + `tool_use` capability
- [ ] `fast_chat` → routes to low-latency chat models
- [ ] `cheap_reasoning` → routes to cost-efficient models with `reasoning` capability
- [ ] `vision_fast` → routes to low-latency models with `vision` capability
- [ ] Capability-based models always pick the best available backend that matches

### Context Window Enforcement
- [ ] Track max context length per model
- [ ] Pre-flight check: reject routing to models with insufficient context window
- [ ] Auto-downgrade to long-context model when needed (configurable)

---

## Phase 5 — Multi-Protocol Compatibility

*Goal: Serve clients using different protocol expectations natively.*

### Anthropic Protocol
- [ ] `/v1/messages` endpoint (Anthropic native format)
- [ ] Anthropic request/response translation layer
- [ ] Claude Code connects without any base URL hack or protocol mismatch
- [ ] Streaming in Anthropic event format

### Ollama Protocol
- [ ] `/api/chat` endpoint (Ollama native format)
- [ ] Ollama request/response translation layer
- [ ] Ollama CLI and clients connect natively

### Protocol Detection
- [ ] Detect incoming protocol from request shape and headers
- [ ] Route to appropriate translation layer automatically
- [ ] Single virtual key works across all protocols

---

## Phase 6 — Live Config & Observability

*Goal: Operate Love AI without ever restarting it.*

### Live Configuration Reload
- [ ] Watch `love_engine_config.yaml` for file changes
- [ ] Parse and validate new config in memory before activating
- [ ] Atomic swap: new config takes effect without dropping in-flight requests
- [ ] Invalid config → rejected silently, old config remains active
- [ ] Admin API endpoint: `POST /admin/api/v1/config/reload`

### Enhanced Admin Dashboard
- [ ] Real-time request log (last N requests, per virtual key or global)
- [ ] Jail state panel: currently jailed backends with cooldown countdowns
- [ ] Backend health panel: latency, success rate, warm/cold status per backend
- [ ] Routing trace: for any request, show which backends were tried and why
- [ ] Live config editor: edit and apply `love_engine_config.yaml` in the UI
- [ ] Usage analytics: token usage, cost, and request count over time

### Metrics & Observability
- [ ] Prometheus metrics endpoint (`/metrics`)
- [ ] Per-request tracking: latency, tokens, retries, failovers, backend used
- [ ] Per-backend health metrics: success rate, avg latency, current jail state
- [ ] Per-virtual-key metrics: requests, spend, RPM current vs limit
- [ ] Streaming metrics: time-to-first-token, total streaming duration
- [ ] Structured logging (JSON) with configurable verbosity

---

## Phase 7 — Usage Tracking & Cost Management

*Goal: Full visibility into AI resource consumption.*

### Token-Level Usage Tracking
- [ ] Track `prompt_tokens`, `completion_tokens`, `total_tokens` per request
- [ ] Track reasoning tokens (where supported by provider)
- [ ] Track cached input tokens (where supported)
- [ ] Associate all tracking with virtual key + project

### Cost Estimation
- [ ] Maintain model price table (`model_prices_and_context_window.json` already present)
- [ ] Real-time cost estimation per request
- [ ] Cumulative cost per virtual key, per project, per provider
- [ ] Budget alerts: notify (log/webhook) when a key approaches its budget cap

### Analytics Storage
- [ ] Persist request logs to SQLite (configurable retention)
- [ ] Aggregate daily/weekly/monthly rollups
- [ ] CSV export for cost reporting

---

## Phase 8 — Security & Project Isolation

*Goal: Practical security for multi-project local environments.*

### Admin API Authentication
- [ ] Admin API (`/admin/api/v1/`) protected by a configurable admin key
- [ ] Admin key stored in environment variable, never in config files
- [ ] Login flow for the admin dashboard

### Virtual Key Expiration
- [ ] `expires_at` field on virtual keys
- [ ] Expired keys rejected at auth layer
- [ ] Admin UI shows expiry status

### Key Scoping Improvements
- [ ] Per-key provider restrictions (not just model restrictions)
- [ ] Per-key tool restrictions (e.g., disable web search for some keys)
- [ ] Per-key IP allowlist (optional, for network-constrained deployments)

---

## Long-Term Vision

Beyond the phases above, Love AI aims to evolve into:

- A **local OpenRouter alternative** — all features of a managed AI routing service, running privately on your own machine with zero data leaving your control
- A **universal AI operating layer** — the single integration point for every AI tool, assistant, and automation workflow you run
- A **self-healing AI infrastructure platform** — a system that monitors, adapts, and recovers without ever needing manual intervention
- A **protocol-compatible AI cloud** — natively speaks OpenAI, Anthropic, Ollama, and future AI protocols from a single endpoint

The end state: every AI application connects to `http://localhost:8000`. Love AI invisibly manages providers, models, keys, failover, routing, reliability, performance, and protocol compatibility — and the applications never need to know.

---

## Versioning

| Version | Milestone |
|---|---|
| v0.x (current) | Core gateway, LiteLLM routing, virtual keys, web search injection, Docker |
| v1.0 | Phase 1-2 complete: multi-key balancing, latency routing, warm models |
| v1.5 | Phase 3-4 complete: advanced jail system, capability routing |
| v2.0 | Phase 5-6 complete: multi-protocol, live config, observability |
| v3.0 | Phase 7-8 complete: full cost tracking, security hardening |
| v∞  | Local OpenRouter alternative — fully self-healing AI cloud |
