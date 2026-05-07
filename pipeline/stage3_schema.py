import requests, json, re, os
API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "openai/gpt-oss-20b:free"
def call_llm(prompt):
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]})
    return r.json()["choices"][0]["message"]["content"]
def generate_schema(architecture: dict) -> dict:
    clean = {k:v for k,v in architecture.items() if not k.startswith("_")}
    text = call_llm(f"Generate complete app schema. Return ONLY valid JSON with ui_schema, api_schema, db_schema, auth_schema keys.\n\nArchitecture: {json.dumps(clean)}").strip()
    text = re.sub(r'^```json\s*', '', text); text = re.sub(r'^```\s*', '', text); text = re.sub(r'\s*```$', '', text)
    result = json.loads(text)
    result["_meta"] = {"stage": "schema_generation", "input_tokens": 0, "output_tokens": 0}
    return result
