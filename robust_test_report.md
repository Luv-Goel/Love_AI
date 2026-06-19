# Robust Gateway Integration Tests

**Total Tests:** 50
**Passed:** 44
**Failed:** 6

## Results Table

| Test Name | Path | Status | Latency (ms) | Result |
|---|---|---|---|---|
| Auth: Missing Header | `/v1/chat/completions` | 401 | 15.06 | ✅ |
| Auth: Invalid Key | `/v1/chat/completions` | 401 | 3.13 | ✅ |
| Auth: Malformed Header 1 | `/v1/chat/completions` | 401 | 2.69 | ✅ |
| Security: Access Admin Root | `/admin/index.html` | 404 | 1.82 | ✅ |
| Security: Access Admin API | `/admin/api/v1/virtual-keys` | 422 | 2.45 | ❌ |
| Security: Directory Traversal | `/../v1/chat` | 500 | 2275.36 | ❌ |
| Security: Null Byte | `/v1/chat%00` | 500 | 244.31 | ❌ |
| Security: Internal Port Scan | `/http://localhost:6666/admin` | 404 | 3.23 | ✅ |
| Security: Options Method | `/v1/chat/completions` | 500 | 2278.83 | ✅ |
| Security: Empty Path | `/` | 404 | 3.15 | ✅ |
| OpenAI: Valid Request | `/v1/chat/completions` | 500 | 2274.41 | ✅ |
| OpenAI: Missing Model | `/v1/chat/completions` | 500 | 2274.78 | ✅ |
| OpenAI: Streaming True | `/v1/chat/completions` | 500 | 2270.89 | ✅ |
| OpenAI: Advanced Params | `/v1/chat/completions` | 500 | 2256.52 | ✅ |
| OpenAI: Empty Messages | `/v1/chat/completions` | 500 | 2281.02 | ✅ |
| OpenAI: Huge Payload | `/v1/chat/completions` | 500 | 2282.64 | ✅ |
| OpenAI: Invalid JSON | `/v1/chat/completions` | 500 | 2288.27 | ❌ |
| OpenAI: Unknown Model | `/v1/chat/completions` | 500 | 2302.72 | ✅ |
| OpenAI: Multi-turn chat | `/v1/chat/completions` | 500 | 2279.81 | ✅ |
| OpenAI: Tool Call Format | `/v1/chat/completions` | 500 | 2274.03 | ✅ |
| Anthropic: Valid Request | `/v1/messages` | 500 | 2284.17 | ✅ |
| Anthropic: Missing Max Tokens | `/v1/messages` | 500 | 2277.45 | ✅ |
| Anthropic: System Prompt | `/v1/messages` | 500 | 2277.4 | ✅ |
| Anthropic: Streaming True | `/v1/messages` | 500 | 2322.45 | ✅ |
| Anthropic: Unknown Model | `/v1/messages` | 500 | 2278.43 | ✅ |
| Anthropic: Multi-turn | `/v1/messages` | 500 | 2267.26 | ✅ |
| Anthropic: Invalid Role | `/v1/messages` | 500 | 2273.8 | ✅ |
| Anthropic: Empty Content | `/v1/messages` | 500 | 2272.69 | ✅ |
| Anthropic: Invalid JSON | `/v1/messages` | 500 | 2274.42 | ❌ |
| Anthropic: Tool Calling Format | `/v1/messages` | 500 | 2281.73 | ✅ |
| Ollama: Valid Request | `/api/generate` | 500 | 2273.45 | ✅ |
| Ollama: Streaming True | `/api/generate` | 500 | 2292.62 | ✅ |
| Ollama: Missing Prompt | `/api/generate` | ERROR | 0 | ❌ |
| Ollama: JSON Format | `/api/generate` | 500 | 2291.24 | ✅ |
| Ollama: Options Params | `/api/generate` | 500 | 2272.3 | ✅ |
| Ollama: Empty Prompt | `/api/generate` | 500 | 2267.63 | ✅ |
| Ollama: Invalid Model | `/api/generate` | 500 | 2263.28 | ✅ |
| Ollama: System Override | `/api/generate` | 500 | 2350.14 | ✅ |
| Ollama: Context Array | `/api/generate` | 500 | 2270.56 | ✅ |
| Ollama: Raw Mode | `/api/generate` | 500 | 2298.19 | ✅ |
| Generic: chat/completions valid | `/chat/completions` | 500 | 2302.12 | ✅ |
| Generic: chat/completions stream | `/chat/completions` | 500 | 2320.23 | ✅ |
| Generic: chat/completions invalid | `/chat/completions` | 500 | 2284.29 | ✅ |
| Generic: responses valid | `/responses` | 500 | 2269.45 | ✅ |
| Generic: responses missing body | `/responses` | 500 | 2272.84 | ✅ |
| Generic: /v1/models (List Models) | `/v1/models` | 500 | 2482.31 | ✅ |
| Generic: /v1/models with body | `/v1/models` | 500 | 2517.96 | ✅ |
| Generic: Non-existent prefix | `/v2/chat` | 404 | 4.03 | ✅ |
| Generic: Just /api | `/api` | 404 | 1.88 | ✅ |
| Generic: Deep invalid path | `/v1/chat/completions/extra` | 500 | 2295.12 | ✅ |

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

### Ollama: Missing Prompt
- Path: `/api/generate`
- Status: ERROR
- Response: ``

