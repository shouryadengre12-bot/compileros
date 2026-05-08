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

from typing import List

def repair_schema(schema: dict, errors: List[str], max_attempts: int = 3) -> dict:
    for attempt in range(max_attempts):
        try:
            clean = {k: v for k, v in schema.items() if not k.startswith("_")}
            result = parse_json(call_llm(f"Fix these errors: {errors}\nSchema: {json.dumps(clean)}\nReturn ONLY valid JSON."))
            result["_meta"] = {"stage": "repair", "attempt": attempt+1, "errors_fixed": errors}
            return result
        except Exception as e:
            if attempt == max_attempts - 1:
                schema["_repair_failed"] = str(e)
                return schema
    return schema

def repair_json_string(text: str) -> str:
    return text.strip()
