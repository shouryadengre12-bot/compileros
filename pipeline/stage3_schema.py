import re
import os

def generate_schema(architecture: dict) -> dict:
    if not isinstance(architecture, dict):
        architecture = {}
    pages = architecture.get("pages", [])
    endpoints = architecture.get("api_endpoints", [])
    entities = architecture.get("entities", [])
    ui_pages = []
    for i, p in enumerate(pages):
        ep_path = next((ep["path"] for ep in endpoints if not "{" in ep.get("path","") and p.get("name","").lower().replace(" ","") in ep.get("path","").lower()), endpoints[0]["path"] if endpoints else "/api/v1/items")
        ui_pages.append({"id": f"page_{i}", "name": p.get("name","Page"), "route": p.get("route","/"), "layout": "sidebar", "components": [{"id": f"comp_{i}", "type": "table", "label": p.get("name","Page"), "data_source": ep_path, "fields": [{"name": "id", "type": "integer", "label": "ID"}, {"name": "name", "type": "string", "label": "Name"}], "actions": [{"label": "Edit", "type": "edit", "endpoint": ep_path}]}], "roles_allowed": p.get("roles_allowed", ["admin"])})
    api_eps = []
    for i, ep in enumerate(endpoints):
        path = ep.get("path", "/api/v1/items")
        table = re.sub(r'\{.*?\}', '', path).strip("/").split("/")[-1] or "items"
        api_eps.append({"id": f"ep_{i}", "method": ep.get("method","GET"), "path": path, "auth_required": ep.get("auth_required", True), "roles": ep.get("roles_allowed", ["admin"]), "request_schema": {}, "response_schema": {}, "db_table": table})
    tables = []
    for entity in entities:
        cols = [{"name": "id", "type": "INT", "primary_key": True, "nullable": False, "unique": True, "foreign_key": None}, {"name": "created_at", "type": "TIMESTAMP", "primary_key": False, "nullable": True, "unique": False, "foreign_key": None}]
        for f in entity.get("fields", []):
            if f.get("name") not in ["id", "created_at"]:
                cols.append({"name": f.get("name","col"), "type": "VARCHAR", "primary_key": False, "nullable": True, "unique": f.get("name") == "email", "foreign_key": None})
        tables.append({"name": entity.get("name","Item").lower()+"s", "columns": cols, "indexes": [{"columns": ["id"], "unique": True}]})
    all_roles = set()
    for p in pages:
        all_roles.update(p.get("roles_allowed", []))
    if not all_roles:
        all_roles = {"admin", "user"}
    result = {
        "ui_schema": {"pages": ui_pages},
        "api_schema": {"base_url": "/api/v1", "endpoints": api_eps},
        "db_schema": {"tables": tables},
        "auth_schema": {"strategy": "JWT", "token_expiry": "24h", "roles": [{"name": r, "permissions": ["read", "write"] if r == "admin" else ["read"]} for r in all_roles], "protected_routes": [{"route": p.get("route","/"), "roles": p.get("roles_allowed",["admin"])} for p in pages if p.get("route") != "/login"]}
    }
    result["_meta"] = {"stage": "schema_generation", "input_tokens": 0, "output_tokens": 0}
    return result
