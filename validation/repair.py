import requests, json, re, os
from typing import List
API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "liquid/lfm-2.5-1.2b-instruct:free"
def call_llm(prompt):
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]})
    return r.json()["choices"][0]["message"]["content"]
def repair_schema(schema: dict, errors: List[str], max_attempts: int = 3) -> dict:
    for attempt in range(max_attempts):
        try:
            clean = {k:v for k,v in schema.items() if not k.startswith("_")}
            text = call_llm(f"Fix these errors: {errors}\n\nSchema: {json.dumps(clean)}\n\nReturn ONLY valid JSON.").strip()
            text = re.sub(r'^```json\s*', '', text); text = re.sub(r'^```\s*', '', text); text = re.sub(r'\s*```$', '', text)
            result = json.loads(text)
            result["_meta"] = {"stage": "repair", "attempt": attempt+1, "errors_fixed": errors}
            return result
        except Exception as e:
            if attempt == max_attempts-1:
                schema["_repair_failed"] = str(e)
                return schema
    return schema
def repair_json_string(text): return text.strip()
