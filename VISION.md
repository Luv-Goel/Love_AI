# Love AI — Complete Project Vision

Love AI is a self-hosted personal AI cloud that sits between your AI applications and multiple AI providers, presenting itself as a single, stable, vendor-agnostic AI platform. Its purpose is to eliminate direct dependency on individual AI vendors and give all local projects one unified endpoint for AI access.

## Core Idea

Instead of every application talking directly to OpenAI, Anthropic, Ollama, NVIDIA NIM, Groq, Google AI Studio, Cerebras, Mistral, local models, or chatbot wrappers, all applications connect only to **Love AI**.

Love AI becomes:
- A local AI cloud
- A universal AI gateway
- A smart routing platform
- A failover system
- A provider abstraction layer
- A protocol-compatible AI hub
- A self-healing AI infrastructure layer

Applications should feel as though they are talking directly to the original provider, while Love AI invisibly manages everything behind the scenes.

---

## Primary Goals

### Protocol Invisibility
Clients should not be able to tell they are using Love AI. Applications such as Claude Code, OpenCode, Hermes, OpenAI SDKs, Anthropic SDKs, Ollama clients, Agent frameworks, and Coding assistants should behave exactly as they would against native providers.

### Stability
Provider outages, model failures, exhausted API keys, and cold starts should be hidden from users whenever possible.

### Resource Efficiency
The system should be lightweight enough to run continuously on a local machine without becoming a resource burden.

### Extensibility
New providers, new virtual models, and new routing strategies should be easy to add over time.

---

## Unified Multi-Vendor AI Cloud
Love AI aggregates many different provider types simultaneously:

- **Cloud Providers**: NVIDIA NIM, Groq, Google AI Studio, Cerebras, Mistral, OpenAI-compatible services, Anthropic-compatible services.
- **Local Providers**: Ollama-based models, Local inference engines.
- **Wrapped Providers**: Services that internally proxy other AI systems, Chatbot wrappers.

All providers become part of one shared AI ecosystem.

---

## Virtual Model System
Users never see raw provider models. Instead, Love AI exposes only virtual models:
- **Vendor-Level Virtual Models**: `vendor_high`, `vendor_mid`, `vendor_low`, `vendor_auto`
- **Global Virtual Models**: `all_high`, `all_mid`, `all_low`, `all_auto`
- **Capability-Based Models**: `code_best`, `fast_chat`, `cheap_reasoning`, `vision_fast`

These become stable AI endpoints regardless of which real model is currently serving them.

---

## Waterfall Routing
Virtual models can contain multiple real models arranged in priority order.
*Example behavior:* Try strongest model. If unavailable, move to next. Continue until success. Never expose backend instability to the client. This creates automatic resilience without requiring user intervention.

---

## Intelligent Provider Selection
Routing decisions can consider:
- Model quality & capability
- Warm status
- Recent latency & failures
- Cold start history
- Vendor health
- Current load & Concurrency levels
- Rate-limit pressure
- Jail state
- Context requirements

The result is adaptive routing rather than static routing.

---

## Virtual API Keys
Projects receive virtual keys instead of real provider credentials. Each virtual key can access selected virtual models, be restricted to certain models, have quotas, have expiration rules, and be isolated from other projects. Applications never see real provider credentials.

---

## Multi-Key Load Balancing
Many providers allow multiple API keys. Love AI can rotate keys automatically, balance requests between keys, spread traffic intelligently, and avoid exhausting a single key. 

Supported concepts include: Round robin, Least used, Random, Weighted balancing, Request-based balancing, Token-based balancing, and Latency-based balancing. Each key can have its own weight in the routing pool.

---

## Rate Limit Awareness
Different vendors have different rate-limit structures. Love AI understands:
- **Shared Limits**: One limit shared across all models.
- **Per-Model Limits**: Separate limits for each model.
- **Group Limits**: Groups of models sharing limits.
- **IP-Based Limits**: Limits applied to the entire connection source.

Routing automatically adapts to each situation.

---

## Warm Model System
Successful model instances become warm. Benefits include reduced cold-start delays, faster future responses, and higher routing preference. Warm models receive temporary preference boosts and remain favored while they are still likely to be loaded and responsive.

---

## Model Pinning
When a model responds successfully, it becomes pinned temporarily. Future requests preferentially reuse it, agent workflows become more stable, and cold starts are reduced. After the pin period ends, normal routing resumes. This balances performance and fairness.

---

## Self-Healing Jail System
Love AI automatically isolates unhealthy resources. Jails exist at multiple levels:
- **Model Jail**: For failing models.
- **API Jail**: For unhealthy API credentials.
- **Vendor Jail**: For failing providers.

Resources are temporarily frozen and removed from routing pools until they recover. 

### Progressive Penalties
Repeated failures increase freeze duration (e.g., First offense, Second offense, etc.). Each offense increases the penalty period until a maximum limit is reached.

### Automatic Recovery
Love AI does not permanently disable resources. Instead it monitors frozen resources, tests them quietly, revalidates health, and reintroduces them gradually.

---

## Unified Streaming System
Streaming works consistently regardless of provider. Capabilities include real-time token streaming, tool-call streaming, incremental responses, structured output streaming, and reasoning output streaming.

---

## Tool Calling Support
Love AI supports modern AI workflows involving tools. Capabilities include tool definitions, tool invocation, tool results, structured tool exchanges, and multi-step agent workflows.

---

## Capability-Aware Routing
Every model advertises capabilities (Chat, Coding, Reasoning, Vision, Embeddings, Multimodal, Tool use, Structured outputs, JSON outputs, Long context). Routing ensures requests only go to compatible models.

---

## Usage Tracking
Love AI maintains detailed accounting. Metrics include: Input/Output/Reasoning/Cached usage, Latency, Retries, Failovers, Provider usage, Project usage, and Virtual key usage. This enables analytics and cost visibility.

---

## Security Features
Love AI includes protected provider credentials, project isolation, virtual keys, usage restrictions, expiration controls, and local-first deployment. The goal is practical security without enterprise complexity.

---

## Live Configuration Management
The system can adapt while running. Capabilities include live configuration updates, routing changes, provider changes, virtual model changes, and validation before activation. Invalid changes never disrupt active operations.

---

## Admin Control Plane
An optional management dashboard provides provider/model/key management, jail/request inspection, routing visualization, live logs, metrics dashboards, usage analytics, warm-model monitoring, and route tracing.

---

## Observability
Love AI continuously exposes operational insight. This includes request tracking, error monitoring, routing metrics, jail metrics, streaming metrics, performance analytics, and health monitoring.

---

## Future Vision
Love AI is intended to evolve into:
- A local OpenRouter alternative
- A universal AI operating layer
- A protocol-compatible AI cloud
- A self-healing AI infrastructure platform
- A centralized AI service hub for all personal and development projects

The end goal is that every AI application connects to a single endpoint, while Love AI invisibly manages providers, models, keys, failover, routing, reliability, performance, and compatibility behind the scenes.
