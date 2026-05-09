import json
import os
from typing import List

def repair_schema(schema: dict, errors: List[str], max_attempts: int = 2) -> dict:
    """Return schema as-is - basic repair without LLM."""
    if not isinstance(schema, dict):
        schema = {}
    schema["_repair_attempted"] = True
    schema["_errors_found"] = errors
    return schema

def repair_json_string(text: str) -> str:
    return text.strip()
