from typing import List

def repair_schema(schema: dict, errors: List[str], max_attempts: int = 2) -> dict:
    if not isinstance(schema, dict):
        schema = {}
    schema["_repair_attempted"] = True
    return schema

def repair_json_string(text: str) -> str:
    return text.strip()
