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
    return response.json()["choices"][0]["message"]["content"]

INTENT_PROMPT = """Extract structured intent from this app description.

Input: {user_input}

Return ONLY valid JSON:
{{
  "app_name": "string",
  "app_type": "string",
  "entities": ["list"],
  "features": ["list"],
  "roles": ["list"],
  "auth_required": true,
  "payment_required": false,
  "ambiguities": ["list"],
  "assumptions": ["list"]
}}"""

def extract_intent(user_input: str) -> dict:
    text = call_llm(INTENT_PROMPT.format(user_input=user_input)).strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    result = json.loads(text)
    result["_meta"] = {"stage": "intent_extraction", "input_tokens": 0, "output_tokens": 0}
    return result
