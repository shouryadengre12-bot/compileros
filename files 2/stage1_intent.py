import anthropic
import json
import re
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

INTENT_PROMPT = """You are a system architect. Extract structured intent from a user's app description.

User Input: {user_input}

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
  "app_name": "string",
  "app_type": "string (e.g. CRM, E-commerce, SaaS, Blog)",
  "entities": ["list of main data entities e.g. User, Product, Order"],
  "features": ["list of features e.g. authentication, payments, dashboard"],
  "roles": ["list of user roles e.g. admin, user, guest"],
  "auth_required": true,
  "payment_required": false,
  "ambiguities": ["list of unclear or missing requirements"],
  "assumptions": ["list of assumptions made to fill gaps"]
}}"""

def extract_intent(user_input: str) -> dict:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": INTENT_PROMPT.format(user_input=user_input)}]
    )
    text = response.content[0].text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    result = json.loads(text)
    result["_meta"] = {
        "stage": "intent_extraction",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }
    return result
