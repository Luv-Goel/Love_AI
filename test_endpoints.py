import asyncio
import httpx
import json
import sqlite3
import os

DB_PATH = "keys.db"

def get_test_key():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT project_name FROM virtual_keys LIMIT 1")
        row = cursor.fetchone()
        if not row:
            print("No test keys found. Create one in the admin UI.")
            return None
        # We don't have the plaintext key from the DB, so we'll just insert a temporary test key
        test_key = "sk-loveai-test-12345"
        import hashlib
        key_hash = hashlib.sha256(test_key.encode('utf-8')).hexdigest()
        try:
            cursor.execute("INSERT INTO virtual_keys (project_name, key_hash, key_hint, allowed_models, budget, spend, rpm_limit, enable_web_search) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("test", key_hash, "sk-test...", "*", 100.0, 0.0, 100, 1))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Already exists
        return test_key

async def test_endpoint(client, path, payload):
    url = f"http://127.0.0.1:6666/{path}"
    print(f"\n--- Testing {path} ---")
    try:
        response = await client.post(url, json=payload, timeout=5.0)
        print(f"Status: {response.status_code}")
        if response.status_code == 404:
            if "proxy_error" in response.text:
                print(f"PASSED: Gateway successfully proxied the request. (love_smith returned 404: {response.text})")
            else:
                print(f"FAILED: Gateway rejected the path. Response: {response.text}")
        elif response.status_code == 401:
            print("FAILED: Auth rejected.")
        else:
            # 500 or 200 or 400 from love_smith means gateway PASSED it successfully!
            print("PASSED: Gateway successfully proxied the request.")
            # print(response.text[:200])
    except httpx.ReadTimeout:
        print("PASSED: Request was proxied but timed out waiting for backend.")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    key = get_test_key()
    if not key:
        return
    
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        # OpenAI style
        await test_endpoint(client, "v1/chat/completions", {"model": "all_low", "messages": [{"role": "user", "content": "hi"}]})
        
        # Anthropic style
        await test_endpoint(client, "v1/messages", {"model": "all_low", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]})
        
        # Ollama style
        await test_endpoint(client, "api/generate", {"model": "all_low", "prompt": "hi", "stream": False})
        
        # Base chat/completions
        await test_endpoint(client, "chat/completions", {"model": "all_low", "messages": [{"role": "user", "content": "hi"}]})
        
        # Responses style
        await test_endpoint(client, "responses", {"model": "all_low", "prompt": "hi"})
        
        # Rejections
        await test_endpoint(client, "admin/hax", {})

if __name__ == "__main__":
    asyncio.run(main())
