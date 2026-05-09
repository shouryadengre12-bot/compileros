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
    # Fix missing commas between } and " or { and "
    text = re.sub(r'}\s*"', '}, "', text)
    text = re.sub(r'"\s*{', '", {', text)
    try:
        return json.loads(text)
    except Exception:
        try:
            import ast
            return ast.literal_eval(text)
        except Exception:
            return {"_parse_error": True, "_raw": text[:200]}

INTENT_PROMPT = """Extract app intent. Return ONLY JSON, no explanation.

App description: {user_input}

JSON format:
{{
  "app_name": "CRM",
  "app_type": "CRM",
  "entities": ["User", "Contact"],
  "features": ["login", "contacts"],
  "roles": ["admin", "user"],
  "auth_required": true,
  "payment_required": false,
  "ambiguities": [],
  "assumptions": []
}}"""

def extract_intent(user_input: str) -> dict:
    result = safe_parse(call_llm(INTENT_PROMPT.format(user_input=user_input)))
    if not isinstance(result, dict):
        result = {"app_name": "App", "app_type": "Web App", "entities": [], "features": [], "roles": ["admin", "user"], "auth_required": True, "payment_required": False, "ambiguities": [], "assumptions": []}
    result["_meta"] = {"stage": "intent_extraction", "input_tokens": 0, "output_tokens": 0}
    return result
