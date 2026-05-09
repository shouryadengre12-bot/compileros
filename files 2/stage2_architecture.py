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

ARCHITECTURE_PROMPT = """Design system architecture. Return ONLY JSON, no explanation.

Intent: {intent}

JSON format:
{{
  "pages": [
    {{"name": "Dashboard", "route": "/dashboard", "components": ["chart", "table"], "roles_allowed": ["admin"], "description": "Main dashboard"}}
  ],
  "api_endpoints": [
    {{"method": "GET", "path": "/api/v1/items", "description": "Get items", "auth_required": true, "roles_allowed": ["admin"], "request_body": {{}}, "response": {{"items": "array"}}}}
  ],
  "entities": [
    {{"name": "User", "description": "App user", "fields": [{{"name": "id", "type": "int", "required": true}}], "relations": []}}
  ],
  "auth_flows": ["email_password", "jwt_token"],
  "business_rules": ["Admins can access all data"]
}}"""

def design_architecture(intent: dict) -> dict:
    clean = {k: v for k, v in intent.items() if not k.startswith("_")}
    result = safe_parse(call_llm(ARCHITECTURE_PROMPT.format(intent=json.dumps(clean))))
    if not isinstance(result, dict) or result.get("_parse_error"):
        result = {
            "pages": [{"name": "Dashboard", "route": "/dashboard", "components": ["table"], "roles_allowed": ["admin"], "description": "Main page"}],
            "api_endpoints": [{"method": "GET", "path": "/api/v1/items", "description": "Get items", "auth_required": True, "roles_allowed": ["admin"], "request_body": {}, "response": {}}],
            "entities": [{"name": "User", "description": "App user", "fields": [{"name": "id", "type": "int", "required": True}], "relations": []}],
            "auth_flows": ["email_password"],
            "business_rules": []
        }
    result["_meta"] = {"stage": "architecture_design", "input_tokens": 0, "output_tokens": 0}
    return result
