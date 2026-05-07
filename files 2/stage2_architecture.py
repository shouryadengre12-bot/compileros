import anthropic
import json
import re
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

ARCHITECTURE_PROMPT = """You are a senior software architect. Given this extracted app intent, design the full system architecture.

Intent:
{intent}

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
  "pages": [
    {{
      "name": "string",
      "route": "string",
      "components": ["list of UI components on this page"],
      "roles_allowed": ["roles that can access this page"],
      "description": "string"
    }}
  ],
  "api_endpoints": [
    {{
      "method": "GET|POST|PUT|DELETE",
      "path": "string e.g. /api/users",
      "description": "string",
      "auth_required": true,
      "roles_allowed": ["list of roles"],
      "request_body": {{"field": "type"}},
      "response": {{"field": "type"}}
    }}
  ],
  "entities": [
    {{
      "name": "string",
      "description": "string",
      "fields": [{{"name": "string", "type": "string", "required": true}}],
      "relations": [{{"type": "has_many|belongs_to|many_to_many", "entity": "string"}}]
    }}
  ],
  "auth_flows": ["list of auth flows"],
  "business_rules": ["list of business logic rules"]
}}"""

def design_architecture(intent: dict) -> dict:
    clean_intent = {k: v for k, v in intent.items() if not k.startswith("_")}
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": ARCHITECTURE_PROMPT.format(intent=json.dumps(clean_intent, indent=2))}]
    )
    text = response.content[0].text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    result = json.loads(text)
    result["_meta"] = {
        "stage": "architecture_design",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }
    return result
