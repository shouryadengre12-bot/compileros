import anthropic
import json
import re
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

REFINEMENT_PROMPT = """You are a consistency auditor. Review this application schema for cross-layer inconsistencies and fix them.

Schema:
{schema}

Check for:
1. UI components referencing API endpoints that don't exist
2. API endpoints referencing DB tables that don't exist
3. Auth roles in UI/API not defined in auth_schema
4. DB tables missing id and created_at columns
5. API fields not matching DB columns

Return ONLY valid JSON with the SAME structure plus a "_refinements" key:
{{
  "_refinements": ["list of changes made"],
  "ui_schema": {{}},
  "api_schema": {{}},
  "db_schema": {{}},
  "auth_schema": {{}}
}}"""

def refine_schema(schema: dict) -> dict:
    clean_schema = {k: v for k, v in schema.items() if not k.startswith("_")}
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        messages=[{"role": "user", "content": REFINEMENT_PROMPT.format(schema=json.dumps(clean_schema, indent=2))}]
    )
    text = response.content[0].text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    result = json.loads(text)
    result["_meta"] = {
        "stage": "refinement",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }
    return result
