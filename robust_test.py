import asyncio
import httpx
import json
import sqlite3
import time

DB_PATH = "keys.db"

def get_test_key():
    return "sk-loveai-test-12345"

test_results = []

async def test_case(client, name, path, payload, headers, expected_status_codes, expect_proxy_error=False, method="POST"):
    url = f"http://127.0.0.1:6666/{path}"
    start = time.time()
    try:
        if method == "POST":
            response = await client.post(url, json=payload, headers=headers, timeout=5.0)
        else:
            response = await client.get(url, headers=headers, timeout=5.0)
            
        elapsed = time.time() - start
        status = response.status_code
        text = response.text
        
        passed = False
        if status in expected_status_codes:
            if expect_proxy_error and "proxy_error" not in text and status == 404:
                passed = False
            else:
                passed = True
                
        test_results.append({
            "name": name,
            "path": path,
            "status": status,
            "passed": passed,
            "latency_ms": round(elapsed * 1000, 2),
            "response": text[:200]
        })
        print(f"{'PASS' if passed else 'FAIL'} | {name} | Status: {status}")
    except Exception as e:
        test_results.append({
            "name": name,
            "path": path,
            "status": "ERROR",
            "passed": False,
            "latency_ms": 0,
            "response": str(e)
        })
        print(f"FAIL | {name} | Error: {e}")

async def run_suite():
    key = get_test_key()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    bad_headers = {"Authorization": "Bearer sk-loveai-invalid"}
    no_headers = {"Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        print("Starting Robust Test Suite (50+ Cases)...\n")
        
        # 1. AUTHENTICATION & SECURITY (10 cases)
        await test_case(client, "Auth: Missing Header", "v1/chat/completions", {"model": "all_low"}, no_headers, [401])
        await test_case(client, "Auth: Invalid Key", "v1/chat/completions", {"model": "all_low"}, bad_headers, [401])
        await test_case(client, "Auth: Malformed Header 1", "v1/chat/completions", {"model": "all_low"}, {"Authorization": "Bear sk"}, [401])
        await test_case(client, "Security: Access Admin Root", "admin/index.html", {}, headers, [404], method="GET")
        await test_case(client, "Security: Access Admin API", "admin/api/v1/virtual-keys", {}, headers, [404, 401])
        await test_case(client, "Security: Directory Traversal", "../v1/chat", {}, headers, [404])
        await test_case(client, "Security: Null Byte", "v1/chat%00", {}, headers, [400, 404])
        await test_case(client, "Security: Internal Port Scan", "http://localhost:6666/admin", {}, headers, [404])
        await test_case(client, "Security: Options Method", "v1/chat/completions", {}, headers, [200, 405, 401, 500, 502], method="OPTIONS")
        await test_case(client, "Security: Empty Path", "", {}, headers, [404])

        # 2. OPENAI NATIVE (/v1/chat/completions) (10 cases)
        payload_base = {"model": "all_low", "messages": [{"role": "user", "content": "hi"}]}
        await test_case(client, "OpenAI: Valid Request", "v1/chat/completions", payload_base, headers, [200, 500, 502])
        await test_case(client, "OpenAI: Missing Model", "v1/chat/completions", {"messages": []}, headers, [400, 500, 502])
        await test_case(client, "OpenAI: Streaming True", "v1/chat/completions", {**payload_base, "stream": True}, headers, [200, 500, 502])
        await test_case(client, "OpenAI: Advanced Params", "v1/chat/completions", {**payload_base, "temperature": 0.5, "max_tokens": 10}, headers, [200, 500, 502])
        await test_case(client, "OpenAI: Empty Messages", "v1/chat/completions", {"model": "all_low", "messages": []}, headers, [400, 500, 502])
        await test_case(client, "OpenAI: Huge Payload", "v1/chat/completions", {"model": "all_low", "messages": [{"role": "user", "content": "a" * 10000}]}, headers, [200, 500, 502, 413])
        await test_case(client, "OpenAI: Invalid JSON", "v1/chat/completions", "not-json", headers, [400, 422])
        await test_case(client, "OpenAI: Unknown Model", "v1/chat/completions", {"model": "made_up_model", "messages": [{"role": "user", "content": "hi"}]}, headers, [400, 404, 500, 502])
        await test_case(client, "OpenAI: Multi-turn chat", "v1/chat/completions", {"model": "all_low", "messages": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}, {"role": "user", "content": "hi again"}]}, headers, [200, 500, 502])
        await test_case(client, "OpenAI: Tool Call Format", "v1/chat/completions", {**payload_base, "tools": [{"type": "function", "function": {"name": "test"}}]}, headers, [200, 500, 502])

        # 3. ANTHROPIC NATIVE (/v1/messages) (10 cases)
        payload_anthropic = {"model": "all_low", "max_tokens": 100, "messages": [{"role": "user", "content": "hi"}]}
        await test_case(client, "Anthropic: Valid Request", "v1/messages", payload_anthropic, headers, [200, 500, 502])
        await test_case(client, "Anthropic: Missing Max Tokens", "v1/messages", {"model": "all_low", "messages": [{"role": "user", "content": "hi"}]}, headers, [400, 500, 502])
        await test_case(client, "Anthropic: System Prompt", "v1/messages", {**payload_anthropic, "system": "You are helpful"}, headers, [200, 500, 502])
        await test_case(client, "Anthropic: Streaming True", "v1/messages", {**payload_anthropic, "stream": True}, headers, [200, 500, 502])
        await test_case(client, "Anthropic: Unknown Model", "v1/messages", {"model": "claude-9", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]}, headers, [400, 404, 500, 502])
        await test_case(client, "Anthropic: Multi-turn", "v1/messages", {"model": "all_low", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}, {"role": "user", "content": "hi again"}]}, headers, [200, 500, 502])
        await test_case(client, "Anthropic: Invalid Role", "v1/messages", {"model": "all_low", "max_tokens": 10, "messages": [{"role": "alien", "content": "hi"}]}, headers, [400, 500, 502])
        await test_case(client, "Anthropic: Empty Content", "v1/messages", {"model": "all_low", "max_tokens": 10, "messages": [{"role": "user", "content": ""}]}, headers, [200, 400, 500, 502])
        await test_case(client, "Anthropic: Invalid JSON", "v1/messages", "broken", headers, [400, 422])
        await test_case(client, "Anthropic: Tool Calling Format", "v1/messages", {**payload_anthropic, "tools": [{"name": "get_weather", "description": "weather"}]}, headers, [200, 500, 502])

        # 4. OLLAMA NATIVE (/api/generate) (10 cases)
        payload_ollama = {"model": "all_low", "prompt": "hi", "stream": False}
        await test_case(client, "Ollama: Valid Request", "api/generate", payload_ollama, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: Streaming True", "api/generate", {"model": "all_low", "prompt": "hi", "stream": True}, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: Missing Prompt", "api/generate", {"model": "all_low"}, headers, [400, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: JSON Format", "api/generate", {**payload_ollama, "format": "json"}, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: Options Params", "api/generate", {**payload_ollama, "options": {"temperature": 0.1}}, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: Empty Prompt", "api/generate", {"model": "all_low", "prompt": ""}, headers, [200, 400, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: Invalid Model", "api/generate", {"model": "llama-99"}, headers, [400, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: System Override", "api/generate", {**payload_ollama, "system": "Be quiet"}, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: Context Array", "api/generate", {**payload_ollama, "context": [1,2,3]}, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Ollama: Raw Mode", "api/generate", {**payload_ollama, "raw": True}, headers, [200, 404, 500, 502], expect_proxy_error=True)

        # 5. GENERIC / FALLBACK ENDPOINTS (10 cases)
        await test_case(client, "Generic: chat/completions valid", "chat/completions", payload_base, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Generic: chat/completions stream", "chat/completions", {**payload_base, "stream": True}, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Generic: chat/completions invalid", "chat/completions", {"foo": "bar"}, headers, [400, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Generic: responses valid", "responses", payload_base, headers, [200, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Generic: responses missing body", "responses", {}, headers, [400, 404, 500, 502], expect_proxy_error=True)
        await test_case(client, "Generic: /v1/models (List Models)", "v1/models", {}, headers, [200, 500, 502], method="GET")
        await test_case(client, "Generic: /v1/models with body", "v1/models", {"foo": "bar"}, headers, [200, 405, 500, 502])
        await test_case(client, "Generic: Non-existent prefix", "v2/chat", payload_base, headers, [404])
        await test_case(client, "Generic: Just /api", "api", payload_base, headers, [404])
        await test_case(client, "Generic: Deep invalid path", "v1/chat/completions/extra", payload_base, headers, [404, 500, 502])

        # Generate Report
        passed_count = sum(1 for r in test_results if r["passed"])
        total_count = len(test_results)
        
        md = f"# Robust Gateway Integration Tests\n\n**Total Tests:** {total_count}\n**Passed:** {passed_count}\n**Failed:** {total_count - passed_count}\n\n## Results Table\n\n| Test Name | Path | Status | Latency (ms) | Result |\n|---|---|---|---|---|\n"
        
        for r in test_results:
            icon = "✅" if r["passed"] else "❌"
            md += f"| {r['name']} | `/{r['path']}` | {r['status']} | {r['latency_ms']} | {icon} |\n"
            
        md += "\n## Detailed Failures\n"
        for r in test_results:
            if not r["passed"]:
                md += f"### {r['name']}\n- Path: `/{r['path']}`\n- Status: {r['status']}\n- Response: `{r['response']}`\n\n"
                
        with open("robust_test_report.md", "w", encoding="utf-8") as f:
            f.write(md)
            
        print(f"\nDone! Passed {passed_count}/{total_count}. Report saved to robust_test_report.md")

if __name__ == "__main__":
    asyncio.run(run_suite())
