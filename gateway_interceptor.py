import json
import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse
from agent_tools import execute_web_search

WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web using love_index for real-time information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "url": {"type": "string", "description": "URL to extract content from (if you want to read a specific page)"}
            },
        }
    }
}

async def handle_reverse_proxy(request: Request, path: str, love_smith_url: str, virtual_key: dict):
    url = f"{love_smith_url}/v1/{path}"
    body = await request.body()
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # 1. Evaluate Capability Policy
    is_chat = (path == "chat/completions" or path == "messages")
    is_stream = False
    req_data = None
    policy = "BYPASS"
    enable_web_search = virtual_key.get("enable_web_search", False)
    
    if is_chat and body:
        try:
            req_data = json.loads(body)
            is_stream = req_data.get("stream", False)
            tools = req_data.get("tools", [])
            has_web_search = any(t.get("function", {}).get("name") == "web_search" for t in tools if isinstance(t, dict))
            
            if enable_web_search:
                if not has_web_search:
                    # Client has no web search harness: inject and intercept
                    tools.append(WEB_SEARCH_TOOL)
                    req_data["tools"] = tools
                    body = json.dumps(req_data).encode('utf-8')
                    headers["content-length"] = str(len(body))
                    policy = "INTERCEPT"
                else:
                    # Client already provided web search: pass through untouched (e.g. Hermes / MCP-aware clients)
                    policy = "BYPASS"
            else:
                # Key toggle disabled: never intercept
                policy = "BYPASS"
        except Exception:
            pass

    client = httpx.AsyncClient(timeout=300.0)
    
    req = client.build_request(
        method=request.method,
        url=url,
        headers=headers,
        content=body,
        params=request.query_params
    )
    
    res = await client.send(req, stream=True)
    
    if is_chat and is_stream and req_data is not None:
        async def stream_interceptor(initial_res):
            print("DEBUG INTERCEPTOR: Started stream_interceptor generator!", flush=True)
            res = initial_res
            current_req_data = req_data
            current_headers = headers
            iterations = 0
            
            while True:
                iterations += 1
                if iterations > 5:
                    print("DEBUG INTERCEPTOR: Max iterations reached, breaking loop!", flush=True)
                    break
                
                tool_call_id = None
                tool_name = None
                tool_args = ""
                intercepting = False
                finished_without_intercept = True
                
                try:
                    async for line in res.aiter_lines():
                        # print(f"DEBUG INTERCEPTOR: Yielding line: {line[:50]}...", flush=True)
                        if not line.startswith("data: "):
                            if line.strip():
                                yield (line + "\n").encode('utf-8')
                            else:
                                yield b"\n"
                            continue
                        
                        data_str = line[len("data: "):].strip()
                        if data_str == "[DONE]":
                            if intercepting:
                                finished_without_intercept = False
                                break
                            else:
                                yield (line + "\n").encode('utf-8')
                                continue
                        
                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                # Only print occasionally to reduce log spam
                                # print(f"DEBUG INTERCEPTOR: policy={policy}, delta={delta}", flush=True)
                                
                                if "tool_calls" in delta and delta["tool_calls"]:
                                    tcall = delta["tool_calls"][0]
                                    if "id" in tcall:
                                        tool_call_id = tcall["id"]
                                    func = tcall.get("function", {})
                                    if "name" in func:
                                        tool_name = func["name"]
                                        if tool_name == "web_search" and policy == "INTERCEPT":
                                            intercepting = True
                                            print("DEBUG INTERCEPTOR: intercepting is now TRUE!", flush=True)
                                    if intercepting and "arguments" in func:
                                        tool_args += func["arguments"]
                                        
                                    if intercepting:
                                        continue # Suppress output
                        except json.JSONDecodeError:
                            pass
                        
                        if not intercepting:
                            yield (line + "\n").encode('utf-8')
                finally:
                    await res.aclose()
                
                if finished_without_intercept:
                    break
                
                # Execute the tool
                try:
                    args_dict = json.loads(tool_args)
                except Exception:
                    args_dict = {}
                
                print("DEBUG INTERCEPTOR: executing web search...", flush=True)
                tool_result = await execute_web_search(args_dict)
                print(f"DEBUG INTERCEPTOR: web search finished. len={len(tool_result)}", flush=True)
                
                # Build a new request
                current_req_data.setdefault("messages", []).append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": tool_args
                        }
                    }]
                })
                current_req_data["messages"].append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": tool_result
                })
                
                new_body = json.dumps(current_req_data).encode('utf-8')
                current_headers = dict(current_headers)
                current_headers["content-length"] = str(len(new_body))
                
                new_request = client.build_request(
                    method=request.method,
                    url=url,
                    headers=current_headers,
                    content=new_body,
                    params=request.query_params
                )
                
                print("DEBUG INTERCEPTOR: sending recursive secondary request...", flush=True)
                res = await client.send(new_request, stream=True)
                print("DEBUG INTERCEPTOR: recursive secondary request sent successfully!", flush=True)
                
            await client.aclose()

        resp_headers = dict(res.headers)
        resp_headers.pop("content-length", None)
        resp_headers.pop("content-encoding", None)
        
        return StreamingResponse(
            stream_interceptor(res),
            status_code=res.status_code,
            headers=resp_headers,
            background=None
        )
    else:
        resp_headers = dict(res.headers)
        resp_headers.pop("content-length", None)
        resp_headers.pop("content-encoding", None)
        return StreamingResponse(
            res.aiter_raw(),
            status_code=res.status_code,
            headers=resp_headers,
            background=client.aclose
        )
