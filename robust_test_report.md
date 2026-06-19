# Robust Gateway Integration Tests

**Total Tests:** 50
**Passed:** 45
**Failed:** 5

## Results Table

| Test Name | Path | Status | Latency (ms) | Result |
|---|---|---|---|---|
| Auth: Missing Header | `/v1/chat/completions` | 401 | 20.85 | ✅ |
| Auth: Invalid Key | `/v1/chat/completions` | 401 | 3.61 | ✅ |
| Auth: Malformed Header 1 | `/v1/chat/completions` | 401 | 3.3 | ✅ |
| Security: Access Admin Root | `/admin/index.html` | 404 | 2.17 | ✅ |
| Security: Access Admin API | `/admin/api/v1/virtual-keys` | 422 | 2.51 | ❌ |
| Security: Directory Traversal | `/../v1/chat` | 500 | 2442.9 | ❌ |
| Security: Null Byte | `/v1/chat%00` | 500 | 437.47 | ❌ |
| Security: Internal Port Scan | `/http://localhost:6666/admin` | 404 | 6.47 | ✅ |
| Security: Options Method | `/v1/chat/completions` | 500 | 2444.53 | ✅ |
| Security: Empty Path | `/` | 404 | 5.49 | ✅ |
| OpenAI: Valid Request | `/v1/chat/completions` | 500 | 2456.61 | ✅ |
| OpenAI: Missing Model | `/v1/chat/completions` | 500 | 2551.44 | ✅ |
| OpenAI: Streaming True | `/v1/chat/completions` | 500 | 2437.02 | ✅ |
| OpenAI: Advanced Params | `/v1/chat/completions` | 500 | 2464.18 | ✅ |
| OpenAI: Empty Messages | `/v1/chat/completions` | 500 | 2461.64 | ✅ |
| OpenAI: Huge Payload | `/v1/chat/completions` | 500 | 2446.01 | ✅ |
| OpenAI: Invalid JSON | `/v1/chat/completions` | 500 | 2443.64 | ❌ |
| OpenAI: Unknown Model | `/v1/chat/completions` | 500 | 2456.34 | ✅ |
| OpenAI: Multi-turn chat | `/v1/chat/completions` | 500 | 2461.56 | ✅ |
| OpenAI: Tool Call Format | `/v1/chat/completions` | 500 | 2474.09 | ✅ |
| Anthropic: Valid Request | `/v1/messages` | 500 | 2449.12 | ✅ |
| Anthropic: Missing Max Tokens | `/v1/messages` | 500 | 2450.2 | ✅ |
| Anthropic: System Prompt | `/v1/messages` | 500 | 2430.84 | ✅ |
| Anthropic: Streaming True | `/v1/messages` | 500 | 2430.15 | ✅ |
| Anthropic: Unknown Model | `/v1/messages` | 500 | 2335.46 | ✅ |
| Anthropic: Multi-turn | `/v1/messages` | 500 | 2347.27 | ✅ |
| Anthropic: Invalid Role | `/v1/messages` | 500 | 2489.64 | ✅ |
| Anthropic: Empty Content | `/v1/messages` | 500 | 2506.51 | ✅ |
| Anthropic: Invalid JSON | `/v1/messages` | 500 | 2447.38 | ❌ |
| Anthropic: Tool Calling Format | `/v1/messages` | 500 | 2450.39 | ✅ |
| Ollama: Valid Request | `/api/generate` | 500 | 2495.8 | ✅ |
| Ollama: Streaming True | `/api/generate` | 500 | 2448.23 | ✅ |
| Ollama: Missing Prompt | `/api/generate` | 500 | 2466.83 | ✅ |
| Ollama: JSON Format | `/api/generate` | 500 | 2451.06 | ✅ |
| Ollama: Options Params | `/api/generate` | 500 | 2271.79 | ✅ |
| Ollama: Empty Prompt | `/api/generate` | 500 | 2307.17 | ✅ |
| Ollama: Invalid Model | `/api/generate` | 500 | 2305.14 | ✅ |
| Ollama: System Override | `/api/generate` | 500 | 2302.02 | ✅ |
| Ollama: Context Array | `/api/generate` | 500 | 2273.38 | ✅ |
| Ollama: Raw Mode | `/api/generate` | 500 | 2276.39 | ✅ |
| Generic: chat/completions valid | `/chat/completions` | 500 | 2297.23 | ✅ |
| Generic: chat/completions stream | `/chat/completions` | 500 | 2297.42 | ✅ |
| Generic: chat/completions invalid | `/chat/completions` | 500 | 2274.12 | ✅ |
| Generic: responses valid | `/responses` | 500 | 2268.01 | ✅ |
| Generic: responses missing body | `/responses` | 500 | 2271.02 | ✅ |
| Generic: /v1/models (List Models) | `/v1/models` | 500 | 2274.12 | ✅ |
| Generic: /v1/models with body | `/v1/models` | 500 | 2273.47 | ✅ |
| Generic: Non-existent prefix | `/v2/chat` | 404 | 2.87 | ✅ |
| Generic: Just /api | `/api` | 404 | 1.66 | ✅ |
| Generic: Deep invalid path | `/v1/chat/completions/extra` | 500 | 2291.59 | ✅ |

## Detailed Failures
### Security: Access Admin API
- Path: `/admin/api/v1/virtual-keys`
- Status: 422
- Response: `{"detail":[{"type":"missing","loc":["body","project_name"],"msg":"Field required","input":{}}]}`

### Security: Directory Traversal
- Path: `/../v1/chat`
- Status: 500
- Response: `Internal Server Error`

### Security: Null Byte
- Path: `/v1/chat%00`
- Status: 500
- Response: `Internal Server Error`

### OpenAI: Invalid JSON
- Path: `/v1/chat/completions`
- Status: 500
- Response: `Internal Server Error`

### Anthropic: Invalid JSON
- Path: `/v1/messages`
- Status: 500
- Response: `Internal Server Error`

