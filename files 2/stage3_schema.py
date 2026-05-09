import requests
import json
import re
import os

API_KEY = os.environ.get("OPENROUTER_API_KEY", "test")
MODEL = "liquid/lfm-2.5-1.2b-instruct:free"

def call_llm(prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    )
    data = response.json()
    if "choices" not in data:
        raise Exception(f"API Error: {data}")
    return data["choices"][0]["message"]["content"]

def safe_parse(text):
    if isinstance(text, dict):
        return text
    text = str(text).strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    try:
        return json.loads(text)
    except Exception:
        return {"_parse_error": True}

def default_schema(architecture):
    pages = architecture.get("pages", [{"name": "Dashboard", "route": "/dashboard"}])
    endpoints = architecture.get("api_endpoints", [])
    entities = architecture.get("entities", [])
    
    return {
        "ui_schema": {
            "pages": [{"id": f"p{i}", "name": p.get("name", "Page"), "route": p.get("route", "/"), "layout": "sidebar", "components": [{"id": f"c{i}", "type": "table", "label": p.get("name", "Page"), "data_source": "/api/v1/items", "fields": [], "actions": []}], "roles_allowed": p.get("roles_allowed", ["admin"])} for i, p in enumerate(pages)]
        },
        "api_schema": {
            "base_url": "/api/v1",
            "endpoints": [{"id": f"e{i}", "method": ep.get("method", "GET"), "path": ep.get("path", "/api/v1/items"), "auth_required": ep.get("auth_required", True), "roles": ep.get("roles_allowed", ["admin"]), "request_schema": {}, "response_schema": {}, "db_table": ep.get("path", "/api/v1/items").split("/")[-1]} for i, ep in enumerate(endpoints)]
        },
        "db_schema": {
            "tables": [{"name": e.get("name", "items").lower(), "columns": [{"name": "id", "type": "INT", "primary_key": True, "nullable": False, "unique": True, "foreign_key": None}, {"name": "created_at", "type": "TIMESTAMP", "primary_key": False, "nullable": True, "unique": False, "foreign_key": None}] + [{"name": f.get("name", "field"), "type": "VARCHAR", "primary_key": False, "nullable": True, "unique": False, "foreign_key": None} for f in e.get("fields", []) if f.get("name") != "id"], "indexes": []} for e in entities]
        },
        "auth_schema": {
            "strategy": "JWT",
            "token_expiry": "24h",
            "roles": [{"name": "admin", "permissions": ["items:read", "items:write", "items:delete"]}, {"name": "user", "permissions": ["items:read"]}],
            "protected_routes": [{"route": p.get("route", "/"), "roles": p.get("roles_allowed", ["admin"])} for p in pages]
        }
    }

SCHEMA_PROMPT = """Generate app schema. Return ONLY JSON, no explanation.

Architecture summary: {arch_summary}

Return JSON with exactly these 4 keys: ui_schema, api_schema, db_schema, auth_schema.
Each must have the correct nested structure with pages, endpoints, tables, and roles."""

def generate_schema(architecture: dict) -> dict:
    clean = {k: v for k, v in architecture.items() if not k.startswith("_")}
    arch_summary = f"Pages: {[p.get('name') for p in clean.get('pages', [])]}, Entities: {[e.get('name') for e in clean.get('entities', [])]}, Endpoints: {len(clean.get('api_endpoints', []))}"
    
    result = safe_parse(call_llm(SCHEMA_PROMPT.format(arch_summary=arch_summary)))
    
    # Validate result has required keys
    if not isinstance(result, dict) or result.get("_parse_error") or not all(k in result for k in ["ui_schema", "api_schema", "db_schema", "auth_schema"]):
        result = default_schema(clean)
    
    result["_meta"] = {"stage": "schema_generation", "input_tokens": 0, "output_tokens": 0}
    return result
