import requests
import json
import re
import os
from json_repair import repair_json

API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "liquid/lfm-2.5-1.2b-instruct:free"

def call_llm(prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={{"Authorization": f"Bearer {{API_KEY}}", "Content-Type": "application/json"}},
        json={{"model": MODEL, "messages": [{{"role": "user", "content": prompt}}]}}
    )
    data = response.json()
    if "choices" not in data:
        raise Exception(f"API Error: {{data}}")
    return data["choices"][0]["message"]["content"]

def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    repaired = repair_json(text)
    if isinstance(repaired, str):
        result = json.loads(repaired)
    else:
        result = repaired
    if not isinstance(result, dict):
        raise ValueError(f"Expected dict, got {{type(result)}}")
    return result

PROMPT = """Generate complete app schema from this architecture.
Architecture: {architecture}
Return ONLY valid JSON with keys: ui_schema, api_schema, db_schema, auth_schema"""

def generate_schema(architecture: dict) -> dict:
    clean = {k: v for k, v in architecture.items() if not k.startswith("_")}
    result = parse_json(call_llm(PROMPT.format(architecture=json.dumps(clean))))
    result["_meta"] = {"stage": "schema_generation", "input_tokens": 0, "output_tokens": 0}
    return result
