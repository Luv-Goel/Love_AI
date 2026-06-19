import os
import sqlite3
import hashlib
import secrets
import json
import httpx
import yaml
from contextlib import asynccontextmanager
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException, Security, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "keys.db")
love_smith_URL = "http://127.0.0.1:6665"
love_engine_CONFIG_PATH = os.path.join(BASE_DIR, "love_engine_config.yaml")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend", "dist")

# Database Init
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS virtual_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                key_hint TEXT NOT NULL,
                allowed_models TEXT NOT NULL,
                budget REAL,
                spend REAL DEFAULT 0.0,
                rpm_limit INTEGER
            )
        ''')
        # Add column if not exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(virtual_keys)")
        columns = [row[1] for row in cursor.fetchall()]
        if "enable_web_search" not in columns:
            cursor.execute("ALTER TABLE virtual_keys ADD COLUMN enable_web_search BOOLEAN DEFAULT 0")
        conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

from fastapi.responses import RedirectResponse

@app.get("/")
def read_root():
    return RedirectResponse(url="/admin/index.html")

# Pydantic Models
class CreateKeyRequest(BaseModel):
    project_name: str
    allowed_models: str = "*"
    budget: Optional[float] = None
    rpm_limit: Optional[int] = None
    enable_web_search: bool = False

# Dependency for Auth
def verify_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(status_code=401, detail={"error": {"message": "Missing Authorization header", "type": "invalid_request_error"}})
    
    token = api_key_header.replace("Bearer ", "").strip()
    key_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, allowed_models, enable_web_search FROM virtual_keys WHERE key_hash = ?", (key_hash,))
        row = cursor.fetchone()
        
    if not row:
        raise HTTPException(status_code=401, detail={"error": {"message": "Invalid API key", "type": "invalid_request_error"}})
    
    return {"id": row[0], "allowed_models": row[1], "enable_web_search": bool(row[2])}

# Admin Endpoints (Matching the Frontend UI expectations)
@app.post("/admin/api/v1/virtual-keys")
def create_virtual_key(req: CreateKeyRequest):
    project_name = req.project_name.strip()
    if not project_name:
        raise HTTPException(status_code=400, detail="project_name is required")
        
    random_part = secrets.token_hex(16)
    short_name = "".join(project_name.lower().split())[:10]
    plaintext_key = f"sk-loveai-{short_name}-{random_part}"
    
    key_hash = hashlib.sha256(plaintext_key.encode('utf-8')).hexdigest()
    key_hint = plaintext_key[:len(f"sk-loveai-{short_name}-")+5] + "..."
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO virtual_keys (project_name, key_hash, key_hint, allowed_models, budget, spend, rpm_limit, enable_web_search) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (project_name, key_hash, key_hint, req.allowed_models, req.budget, 0.0, req.rpm_limit, req.enable_web_search)
        )
        conn.commit()
        key_id = cursor.lastrowid
        
    return {
        "id": key_id,
        "project_name": project_name,
        "api_key": plaintext_key,
        "key_hint": key_hint,
        "budget": req.budget,
        "spend": 0.0,
        "rpm_limit": req.rpm_limit,
        "enable_web_search": req.enable_web_search
    }

@app.get("/admin/api/v1/virtual-keys")
def list_virtual_keys():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, project_name, key_hint, allowed_models, budget, spend, rpm_limit, enable_web_search FROM virtual_keys")
        rows = cursor.fetchall()
        
    return [dict(row) for row in rows]

@app.delete("/admin/api/v1/virtual-keys/{key_id}")
def delete_virtual_key(key_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM virtual_keys WHERE id = ?", (key_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        conn.commit()
    return {"status": "deleted"}

@app.get("/admin/api/v1/providers")
def list_providers():
    try:
        with open(love_engine_CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
            # Map model_list to the frontend's expected provider format
            # e.g. [{"id": "vllm", "name": "vLLM", "base_url": "...", "api_key_count": 1, "enabled": true}]
            # We will just synthesize one provider for the YAML file for now
            return [{
                "id": "love_engine_config",
                "name": "love_engine YAML Config",
                "base_url": "love_engine_config.yaml",
                "api_key_count": len(config.get("model_list", [])),
                "enabled": True
            }]
    except Exception as e:
        return []

@app.get("/admin/api/v1/routing-rules")
def list_routing_rules():
    try:
        with open(love_engine_CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
            fallbacks = config.get("router_settings", {}).get("fallbacks", [])
            rules = []
            id_counter = 1
            for fb_group in fallbacks:
                for vm, fallback_list in fb_group.items():
                    for idx, fb_model in enumerate(fallback_list):
                        rules.append({
                            "id": id_counter,
                            "virtual_model": vm,
                            "vendor": "love_engine",
                            "model_name": fb_model,
                            "priority": idx + 1,
                            "weight": 100,
                            "enabled": True
                        })
                        id_counter += 1
            return rules
    except Exception as e:
        return []

@app.get("/admin/api/v1/virtual-models")
def list_virtual_models():
    try:
        with open(love_engine_CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
            return [{"name": m.get("model_name")} for m in config.get("model_list", [])]
    except Exception as e:
        return {"error": str(e)}

@app.get("/admin/api/v1/jails")
def list_jails():
    return []

# --- Missing Provider Stubs ---
@app.get("/admin/api/v1/providers/{vId}/keys")
def get_provider_keys(vId: str): return []
@app.post("/admin/api/v1/providers/{vId}/keys")
def add_provider_key(vId: str, p: dict): return {"status": "ok"}
@app.delete("/admin/api/v1/keys/{id}")
def delete_provider_key(id: str): return {"status": "ok"}

@app.get("/admin/api/v1/providers/{vId}/models")
def get_provider_models(vId: str): return []
@app.post("/admin/api/v1/providers/{vId}/models")
def add_provider_model(vId: str, p: dict): return {"status": "ok"}
@app.delete("/admin/api/v1/models/{id}")
def delete_provider_model(id: str): return {"status": "ok"}

@app.get("/admin/api/v1/providers/{vId}/model-groups")
def get_provider_groups(vId: str): return []
@app.post("/admin/api/v1/providers/{vId}/model-groups")
def add_provider_group(vId: str, p: dict): return {"status": "ok"}
@app.delete("/admin/api/v1/model-groups/{id}")
def delete_provider_group(id: str): return {"status": "ok"}
@app.get("/admin/api/v1/model-groups/{id}/members")
def get_group_members(id: str): return []
@app.post("/admin/api/v1/model-groups/{id}/members")
def set_group_members(id: str, p: dict): return {"status": "ok"}

# --- Missing Routing Rule Stubs ---
@app.post("/admin/api/v1/routing-rules")
def create_routing_rule(p: dict): return {"status": "ok"}
@app.put("/admin/api/v1/routing-rules/{id}")
def update_routing_rule(id: str, p: dict): return {"status": "ok"}
@app.delete("/admin/api/v1/routing-rules/{id}")
def delete_routing_rule(id: str): return {"status": "ok"}
@app.post("/admin/api/v1/routing-rules/sync-individual")
def sync_individual_models(): return {"status": "ok"}

@app.get("/admin/api/v1/metrics-summary")
def get_metrics_summary():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(spend) FROM virtual_keys")
        total_spend = cursor.fetchone()[0] or 0.0
    return {"total_spend": total_spend, "requests_today": 0}

@app.get("/admin/api/v1/logs")
def get_logs():
    return [{"timestamp": "Now", "message": "Logs coming soon..."}]

# Rate Limits stubs mapping to SQLite Virtual Keys
@app.get("/admin/api/v1/limits/{limit_type}/{entity_id}")
def get_rate_limits(limit_type: str, entity_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rpm_limit FROM virtual_keys WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Key not found")
        limits = []
        if row[0]:
            limits.append({"limit_type": "requests", "window_size": "minute", "max_value": row[0], "id": entity_id})
        return limits

class RateLimitUpdate(BaseModel):
    limit_type: str
    window_size: str
    max_value: int

@app.put("/admin/api/v1/limits/{limit_type}/{entity_id}")
def upsert_rate_limit(limit_type: str, entity_id: int, req: RateLimitUpdate):
    if req.limit_type == "requests":
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE virtual_keys SET rpm_limit = ? WHERE id = ?", (req.max_value, entity_id))
            conn.commit()
    return {"status": "ok"}

@app.delete("/admin/api/v1/limits/{limit_type}/{entity_id}/{limitT}/{ws}")
def delete_rate_limit(limit_type: str, entity_id: int, limitT: str, ws: str):
    if limitT == "requests":
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE virtual_keys SET rpm_limit = NULL WHERE id = ?", (entity_id,))
            conn.commit()
    return {"status": "ok"}

from gateway_interceptor import handle_reverse_proxy

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def reverse_proxy(request: Request, path: str):
    if path.startswith("admin") or path == "":
        raise HTTPException(status_code=404, detail="Not Found")
    
    allowed_prefixes = ("v1/", "api/generate", "chat/completions", "responses")
    if not any(path.startswith(p) for p in allowed_prefixes):
        raise HTTPException(status_code=404, detail="Not Found")

    v_key = verify_api_key(request.headers.get("Authorization", ""))
    return await handle_reverse_proxy(request, path, love_smith_URL, v_key)

if os.path.exists(FRONTEND_DIR):
    app.mount("/admin", StaticFiles(directory=FRONTEND_DIR, html=True), name="admin_frontend")
else:
    @app.get("/admin")
    def admin_not_built():
        return {"error": "Frontend not built yet. Run npm run build in frontend/."}
