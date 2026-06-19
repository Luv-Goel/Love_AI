<div align="center">

# 🌸 Love AI

### Your Personal AI Cloud

**One endpoint. Every model. Infinite resilience. Runs on your machine.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-Alpha-orange)]()

[**What is Love AI?**](#-what-is-love-ai) · [**Architecture**](#-architecture) · [**Features**](#-features-in-depth) · [**Virtual Models**](#-the-virtual-model-system) · [**Quick Start**](#-quick-start)

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
                      │ http://localhost:6666
                      │ (Supports OpenAI, Anthropic, Ollama payloads natively)
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
```

---

## 🏗️ Architecture

Love AI is composed of specialized subsystems:

| Subsystem | Role |
|-----------|------|
| **Love Gate (Gateway)** | The front door — virtual key authentication, per-project isolation, proxy routing, usage accounting |
| **Love Watch** | The interceptor — inspects streaming responses, detects tool calls, executes them server-side |
| **Love Smith** | The router — dispatches requests to the right provider, manages fallbacks, rate limits, and health |
| **Love Engine** | The translator — converts OpenAI-formatted requests to natively interface with Anthropic, Bedrock, Vertex, etc. |
| **Love Index** *(Alpha)* | Private search engine — fully self-hosted, no external search APIs. Currently undergoing implementation updates. |
| **Love Crawler** *(Alpha)*| Content extractor — fetches and distills web pages into LLM-digestible text. Currently undergoing implementation updates. |

---

## ✨ Features In Depth

### 🔌 Multi-Protocol Native Proxying
Love AI goes beyond just intercepting standard OpenAI requests. The **Love Gate** intercepts and dynamically translates multiple backend protocols seamlessly:
- **OpenAI-Compatible (`/v1/chat/completions`)**: Fully supported.
- **Anthropic Native (`/v1/messages`)**: Intercepted and mapped automatically.
- **Ollama Native (`/api/generate`)**: Intercepted and routed natively.
- **Generic Completion endpoints (`/chat/completions`, `/responses`)**: Intercepted and mapped seamlessly.

### 🔑 Virtual Key Management
Every project receives a `sk-loveai-*` virtual key. Real vendor credentials (NVIDIA, Anthropic, OpenAI, etc.) are stored locally and **never exposed**. Each virtual key carries:
- Allowed virtual models, Budget cap (spend limit), RPM quotas, and Web Search toggles.

### 🔀 Intelligent Model Routing & Fallbacks
Love Smith supports **100+ providers** and manages **Waterfall fallback chains**. If `meta/llama-3.1-405b` fails via NVIDIA NIM, Love AI silently drops down to `meta/llama-3.1-70b` or completely routes over to Groq or Mistral.

### 🔒 Self-Healing Jail System
Love AI automatically isolates failing resources with progressive penalties. Jails exist at three levels — individual model instances, API keys, and entire vendor backends. Love AI quietly probes jailed resources and reintroduces them when they recover. No human intervention required.

### 🧠 The Virtual Model System
Clients never reference raw provider model names. Instead, Love AI exposes **virtual models** — stable endpoints that map to one or more real models behind the scenes:
- **`all_high`**: Routes to the highest-tier reasoning models available (e.g., Llama-3.1-405b, GPT-4o, Claude-3.5-Sonnet)
- **`all_mid`**: Routes to balanced models (e.g., Llama-3.1-70b)
- **`all_low`**: Routes to fast/cheap models (e.g., Llama-3.1-8b, Gemma)
- **`code_best`**: The best available coding model.

---

## 🚀 Quick Start

### 1. Configure Your Keys
Add your actual vendor API keys to your environment variables (e.g., `NVIDIA_API_KEY`) or inside `love_engine_config.yaml`.

### 2. Boot the System
Run the provided PowerShell script to launch all subsystems on their local ports:
```powershell
.\start_all.ps1
```

### 3. Generate a Virtual Key
Navigate to `http://127.0.0.1:6666/admin/index.html` (Love Gate Dashboard) to generate your first project key (e.g. `sk-loveai-test-123`).

### 4. Connect Your Apps
Point any AI application, coding assistant, or framework at Love AI.
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:6666/v1",
    api_key="sk-loveai-test-123"
)
```
*(Or point your Anthropic SDK to `http://127.0.0.1:6666` natively!)*

---

*Note: Love Crawler (port 6668) and Love Index (port 8090) are actively being developed and may not boot cleanly on all platforms yet. Check the logs for Java/Docker dependency errors.*
