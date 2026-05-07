import requests, json, re, os
API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "nvidia/nemotron-nano-9b-v2:free"
def call_llm(prompt):
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]})
    return r.json()["choices"][0]["message"]["content"]
def design_architecture(intent: dict) -> dict:
    clean = {k:v for k,v in intent.items() if not k.startswith("_")}
    text = call_llm(f"Design system architecture for this app. Return ONLY valid JSON with pages, api_endpoints, entities, auth_flows, business_rules arrays.\n\nIntent: {json.dumps(clean)}").strip()
    text = re.sub(r'^```json\s*', '', text); text = re.sub(r'^```\s*', '', text); text = re.sub(r'\s*```$', '', text)
    result = json.loads(text)
    result["_meta"] = {"stage": "architecture_design", "input_tokens": 0, "output_tokens": 0}
    return result
