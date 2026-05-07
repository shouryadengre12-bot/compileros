from typing import Tuple, List

REQUIRED_TOP_KEYS = ["ui_schema", "api_schema", "db_schema", "auth_schema"]

def validate_schema(schema: dict) -> Tuple[bool, List[str]]:
    """
    Validate the final schema for required fields and cross-layer consistency.
    Returns (is_valid, list_of_errors)
    """
    errors = []

    # 1. Check top-level keys
    for key in REQUIRED_TOP_KEYS:
        if key not in schema:
            errors.append(f"MISSING_KEY: '{key}' not found in schema")

    if errors:
        return False, errors

    # 2. Validate UI schema
    ui = schema.get("ui_schema", {})
    if not isinstance(ui.get("pages"), list) or len(ui["pages"]) == 0:
        errors.append("UI_ERROR: ui_schema.pages must be a non-empty list")
    else:
        for i, page in enumerate(ui["pages"]):
            for field in ["id", "name", "route", "components"]:
                if field not in page:
                    errors.append(f"UI_ERROR: page[{i}] missing field '{field}'")

    # 3. Validate API schema
    api = schema.get("api_schema", {})
    if not isinstance(api.get("endpoints"), list) or len(api["endpoints"]) == 0:
        errors.append("API_ERROR: api_schema.endpoints must be a non-empty list")
    else:
        api_paths = set()
        for i, ep in enumerate(api["endpoints"]):
            for field in ["method", "path", "auth_required"]:
                if field not in ep:
                    errors.append(f"API_ERROR: endpoint[{i}] missing field '{field}'")
            if "path" in ep:
                api_paths.add(ep["path"])

    # 4. Validate DB schema
    db = schema.get("db_schema", {})
    if not isinstance(db.get("tables"), list) or len(db["tables"]) == 0:
        errors.append("DB_ERROR: db_schema.tables must be a non-empty list")
    else:
        db_tables = set()
        for i, table in enumerate(db["tables"]):
            if "name" not in table:
                errors.append(f"DB_ERROR: table[{i}] missing 'name'")
            if not isinstance(table.get("columns"), list):
                errors.append(f"DB_ERROR: table[{i}] missing 'columns' list")
            else:
                db_tables.add(table["name"])
                col_names = [c.get("name") for c in table["columns"]]
                if "id" not in col_names:
                    errors.append(f"DB_WARNING: table '{table.get('name')}' missing 'id' column")

    # 5. Validate Auth schema
    auth = schema.get("auth_schema", {})
    if "roles" not in auth or not isinstance(auth["roles"], list):
        errors.append("AUTH_ERROR: auth_schema.roles must be a list")
    if "strategy" not in auth:
        errors.append("AUTH_ERROR: auth_schema.strategy missing")

    # 6. Cross-layer: API db_table references must exist in DB
    if "endpoints" in api and "tables" in db:
        db_table_names = {t["name"] for t in db["tables"]}
        for ep in api.get("endpoints", []):
            if "db_table" in ep and ep["db_table"] and ep["db_table"] not in db_table_names:
                errors.append(
                    f"CROSS_LAYER: API endpoint '{ep.get('path')}' references "
                    f"non-existent DB table '{ep['db_table']}'"
                )

    # 7. Cross-layer: UI data_sources must match API paths
    if "pages" in ui and "endpoints" in api:
        api_paths = {ep["path"] for ep in api.get("endpoints", []) if "path" in ep}
        for page in ui.get("pages", []):
            for comp in page.get("components", []):
                ds = comp.get("data_source")
                if ds and ds not in api_paths:
                    errors.append(
                        f"CROSS_LAYER: UI component '{comp.get('id')}' references "
                        f"non-existent API path '{ds}'"
                    )

    is_valid = len(errors) == 0
    return is_valid, errors
