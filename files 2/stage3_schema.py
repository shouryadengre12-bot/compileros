import anthropic
import json
import re
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SCHEMA_PROMPT = """You are a schema engineer. Generate a complete, executable application schema from this architecture.

Architecture:
{architecture}

Return ONLY valid JSON (no markdown, no explanation) with this EXACT structure:
{{
  "ui_schema": {{
    "pages": [
      {{
        "id": "string",
        "name": "string",
        "route": "string",
        "layout": "sidebar|topnav|fullpage",
        "components": [
          {{
            "id": "string",
            "type": "table|form|chart|card|button|input|modal",
            "label": "string",
            "data_source": "string (API endpoint path)",
            "fields": [{{"name": "string", "type": "string", "label": "string"}}],
            "actions": [{{"label": "string", "type": "string", "endpoint": "string"}}]
          }}
        ],
        "roles_allowed": ["list"]
      }}
    ]
  }},
  "api_schema": {{
    "base_url": "/api/v1",
    "endpoints": [
      {{
        "id": "string",
        "method": "string",
        "path": "string",
        "auth_required": true,
        "roles": ["list"],
        "request_schema": {{"field": {{"type": "string", "required": true}}}},
        "response_schema": {{"field": {{"type": "string"}}}},
        "db_table": "string"
      }}
    ]
  }},
  "db_schema": {{
    "tables": [
      {{
        "name": "string",
        "columns": [
          {{
            "name": "string",
            "type": "VARCHAR|INT|BOOLEAN|TEXT|TIMESTAMP|DECIMAL",
            "primary_key": false,
            "nullable": true,
            "unique": false,
            "foreign_key": null
          }}
        ],
        "indexes": [{{"columns": ["list"], "unique": false}}]
      }}
    ]
  }},
  "auth_schema": {{
    "strategy": "JWT",
    "token_expiry": "24h",
    "roles": [
      {{
        "name": "string",
        "permissions": ["list of resource:action strings"]
      }}
    ],
    "protected_routes": [{{"route": "string", "roles": ["list"]}}]
  }}
}}"""

def generate_schema(architecture: dict) -> dict:
    clean_arch = {k: v for k, v in architecture.items() if not k.startswith("_")}
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        messages=[{"role": "user", "content": SCHEMA_PROMPT.format(architecture=json.dumps(clean_arch, indent=2))}]
    )
    text = response.content[0].text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    result = json.loads(text)
    result["_meta"] = {
        "stage": "schema_generation",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }
    return result
