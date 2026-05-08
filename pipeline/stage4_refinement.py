import requests
import json
import re
import os

API_KEY = os.environ["OPENROUTER_API_KEY"]
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

def refine_schema(schema: dict) -> dict:
    clean = {k: v for k, v in schema.items() if not k.startswith("_")}
    try:
        text = call_llm(f"Return this JSON unchanged:\n{json.dumps(clean)}").strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            text = text[start:end]
        result = json.loads(text)
        if not isinstance(result, dict):
            result = clean
    except Exception:
        result = clean
    result["_meta"] = {"stage": "refinement", "input_tokens": 0, "output_tokens": 0}
    result["_refinements"] = ["Schema passed through refinement stage"]
    return result
