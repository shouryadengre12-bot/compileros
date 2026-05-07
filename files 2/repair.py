import anthropic
import json
import re
import os
from typing import List

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

REPAIR_PROMPT = """You are a JSON repair specialist. Fix ONLY the specific errors listed below in this schema.

Schema:
{schema}

Errors to fix:
{errors}

Return ONLY valid JSON with the same top-level structure. No markdown."""

def repair_schema(schema: dict, errors: List[str], max_attempts: int = 3) -> dict:
    all_errors = [e for e in errors if any(e.startswith(p) for p in ["UI_","API_","DB_","AUTH_","CROSS_"])]
    for attempt in range(max_attempts):
        try:
            clean_schema = {k: v for k, v in schema.items() if not k.startswith("_")}
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=3000,
                messages=[{"role": "user", "content": REPAIR_PROMPT.format(
                    schema=json.dumps(clean_schema, indent=2),
                    errors="\n".join(f"- {e}" for e in all_errors)
                )}]
            )
            text = response.content[0].text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'^```\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            repaired = json.loads(text)
            repaired["_meta"] = {"stage": "repair", "attempt": attempt+1, "errors_fixed": all_errors}
            return repaired
        except Exception as e:
            if attempt == max_attempts - 1:
                schema["_repair_failed"] = str(e)
                return schema
    return schema

def repair_json_string(text: str) -> str:
    text = re.sub(r'^```json\s*', '', text.strip())
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = re.sub(r',\s*([}\]])', r'\1', text)
    return text.strip()
