import json
import os

def design_architecture(intent: dict) -> dict:
    if not isinstance(intent, dict):
        intent = {}
    entities = intent.get("entities", ["User", "Item"])
    roles = intent.get("roles", ["admin", "user"])
    features = intent.get("features", ["dashboard"])
    auth = intent.get("auth_required", True)
    payments = intent.get("payment_required", False)
    pages = []
    if auth:
        pages.append({"name": "Login", "route": "/login", "components": ["login_form"], "roles_allowed": ["guest"], "description": "Login page"})
    pages.append({"name": "Dashboard", "route": "/dashboard", "components": ["stats_cards", "chart"], "roles_allowed": roles, "description": "Main dashboard"})
    for f in features:
        if f not in ["login", "dashboard"]:
            pages.append({"name": f.title(), "route": f"/{f}", "components": ["table", "form"], "roles_allowed": roles, "description": f"{f.title()} page"})
    endpoints = []
    for entity in entities:
        base = f"/api/v1/{entity.lower()}s"
        endpoints.append({"method": "GET", "path": base, "description": f"List {entity}s", "auth_required": auth, "roles_allowed": roles, "request_body": {}, "response": {}})
        endpoints.append({"method": "POST", "path": base, "description": f"Create {entity}", "auth_required": auth, "roles_allowed": ["admin"], "request_body": {}, "response": {}})
        endpoints.append({"method": "PUT", "path": f"{base}/{{id}}", "description": f"Update {entity}", "auth_required": auth, "roles_allowed": ["admin"], "request_body": {}, "response": {}})
        endpoints.append({"method": "DELETE", "path": f"{base}/{{id}}", "description": f"Delete {entity}", "auth_required": auth, "roles_allowed": ["admin"], "request_body": {}, "response": {}})
    if auth:
        endpoints.append({"method": "POST", "path": "/api/v1/auth/login", "description": "Login", "auth_required": False, "roles_allowed": ["guest"], "request_body": {"email": "string", "password": "string"}, "response": {"token": "string"}})
    if payments:
        endpoints.append({"method": "POST", "path": "/api/v1/payments/checkout", "description": "Checkout", "auth_required": True, "roles_allowed": roles, "request_body": {"plan": "string"}, "response": {"url": "string"}})
    entity_objs = [{"name": e, "description": f"{e} model", "fields": [{"name": "id", "type": "integer", "required": True}, {"name": "name", "type": "string", "required": True}, {"name": "created_at", "type": "datetime", "required": True}], "relations": []} for e in entities]
    result = {"pages": pages, "api_endpoints": endpoints, "entities": entity_objs, "auth_flows": ["jwt"] if auth else [], "business_rules": ["Admins can create/update/delete", "Users have read-only access"]}
    result["_meta"] = {"stage": "architecture_design", "input_tokens": 0, "output_tokens": 0}
    return result
