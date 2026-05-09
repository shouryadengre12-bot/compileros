import streamlit as st
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_pipeline

st.set_page_config(page_title="CompilerOS", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
.stage-box { background: #1e1e2e; border: 1px solid #313244; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ CompilerOS")
    st.caption("Natural Language → Executable App Schema")
    st.divider()
    st.markdown("### How it works")
    st.markdown("1. **Stage 1** — Extract Intent\n2. **Stage 2** — Design Architecture\n3. **Stage 3** — Generate Schema\n4. **Stage 4** — Refine & Validate\n5. **Repair** — Auto-fix if needed")
    st.divider()
    st.markdown("### Example prompts")
    examples = [
        "Build a CRM with login, contacts, dashboard, and role-based access for admins and sales reps",
        "Create an e-commerce store with product catalog, cart, and Stripe payments",
        "Build a project management tool with boards, tasks, and team collaboration",
    ]
    for ex in examples:
        if st.button(ex[:50] + "...", use_container_width=Tr
cd ~/Desktop/compileros
source ~/.zshrc

python3 << 'PYEOF'
import os

HEADER = '''import requests
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
    data = response.json()
    if "choices" not in data:
        raise Exception(f"API Error: {data}")
    return data["choices"][0]["message"]["content"]

def safe_parse(text):
    """Extract and parse JSON from LLM response, returns dict always."""
    if isinstance(text, dict):
        return text
    text = str(text).strip()
    # Remove markdown
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Find outermost { }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    # Fix trailing commas
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
        return {"data": result}
    except Exception:
        # Last resort - return empty dict with raw text
        return {"_raw": text[:500], "_parse_error": True}
'''

stage1 = HEADER + '''
PROMPT = """You are a system architect. Extract app intent as JSON only.

App: {user_input}

Respond with ONLY this JSON (no other text):
{{"app_name": "name", "app_type": "type", "entities": ["list"], "features": ["list"], "roles": ["list"], "auth_required": true, "payment_required": false, "ambiguities": [], "assumptions": []}}"""

def extract_intent(user_input: str) -> dict:
    result = safe_parse(call_llm(PROMPT.format(user_input=user_input)))
    result["_meta"] = {"stage": "intent_extraction", "input_tokens": 0, "output_tokens": 0}
    return result
'''

stage2 = HEADER + '''
PROMPT = """You are a software architect. Design app architecture as JSON only.

Intent: {intent}

Respond with ONLY this JSON:
{{"pages": [{{"name": "string", "route": "string", "components": [], "roles_allowed": [], "description": "string"}}], "api_endpoints": [{{"method": "GET", "path": "/api/items", "description": "string", "auth_required": true, "roles_allowed": [], "request_body": {{}}, "response": {{}}}}], "entities": [{{"name": "string", "description": "string", "fields": [], "relations": []}}], "auth_flows": [], "business_rules": []}}"""

def design_architecture(intent: dict) -> dict:
    clean = {k: v for k, v in intent.items() if not k.startswith("_")}
    result = safe_parse(call_llm(PROMPT.format(intent=json.dumps(clean))))
    result["_meta"] = {"stage": "architecture_design", "input_tokens": 0, "output_tokens": 0}
    return result
'''

stage3 = HEADER + '''
PROMPT = """You are a schema engineer. Generate app schema as JSON only.

Architecture: {architecture}

Respond with ONLY this JSON:
{{"ui_schema": {{"pages": [{{"id": "p1", "name": "Dashboard", "route": "/dashboard", "layout": "sidebar", "components": [], "roles_allowed": []}}]}}, "api_schema": {{"base_url": "/api/v1", "endpoints": [{{"id": "e1", "method": "GET", "path": "/api/v1/items", "auth_required": true, "roles": [], "request_schema": {{}}, "response_schema": {{}}, "db_table": "items"}}]}}, "db_schema": {{"tables": [{{"name": "items", "columns": [{{"name": "id", "type": "INT", "primary_key": true, "nullable": false, "unique": true, "foreign_key": null}}, {{"name": "created_at", "type": "TIMESTAMP", "primary_key": false, "nullable": true, "unique": false, "foreign_key": null}}], "indexes": []}}]}}, "auth_schema": {{"strategy": "JWT", "token_expiry": "24h", "roles": [{{"name": "admin", "permissions": ["items:read", "items:write"]}}], "protected_routes": [{{"route": "/dashboard", "roles": ["admin"]}}]}}}}"""

def generate_schema(architecture: dict) -> dict:
    clean = {k: v for k, v in architecture.items() if not k.startswith("_")}
    result = safe_parse(call_llm(PROMPT.format(architecture=json.dumps(clean))))
    result["_meta"] = {"stage": "schema_generation", "input_tokens": 0, "output_tokens": 0}
    return result
'''

stage4 = HEADER + '''
def refine_schema(schema: dict) -> dict:
    """Pass through schema without LLM to avoid parsing issues."""
    if not isinstance(schema, dict):
        schema = {}
    clean = {k: v for k, v in schema.items() if not k.startswith("_")}
    clean["_meta"] = {"stage": "refinement", "input_tokens": 0, "output_tokens": 0}
    clean["_refinements"] = ["Schema passed through refinement stage"]
    return clean
'''

repair_content = HEADER + '''
from typing import List

def repair_schema(schema: dict, errors: List[str], max_attempts: int = 2) -> dict:
    if not isinstance(schema, dict):
        schema = {}
    for attempt in range(max_attempts):
        try:
            clean = {k: v for k, v in schema.items() if not k.startswith("_")}
            prompt = f"Fix these JSON schema errors: {errors[:3]}\\n\\nSchema: {json.dumps(clean)[:1000]}\\n\\nReturn ONLY valid JSON."
            result = safe_parse(call_llm(prompt))
            if isinstance(result, dict) and not result.get("_parse_error"):
                result["_meta"] = {"stage": "repair", "attempt": attempt+1, "errors_fixed": errors}
                return result
        except Exception as e:
            if attempt == max_attempts - 1:
                schema["_repair_failed"] = str(e)
                return schema
    return schema

def repair_json_string(text: str) -> str:
    return text.strip()
'''

files = {
    "pipeline/stage1_intent.py": stage1,
    "pipeline/stage2_architecture.py": stage2,
    "pipeline/stage3_schema.py": stage3,
    "pipeline/stage4_refinement.py": stage4,
    "validation/repair.py": repair_content,
}

for path, content in files.items():
    with open(path, "w") as f:
        f.write(content)
    print(f"Written: {path}")

print("All done!")
PYEOF

git add .
git commit -m "Bulletproof JSON parsing - always returns dict"
git push origin main
cd ~/Desktop/compileros
mv ~/Desktop/stage1_intent.py pipeline/stage1_intent.py
mv ~/Desktop/stage2_architecture.py pipeline/stage2_architecture.py
mv ~/Desktop/stage3_schema.py pipeline/stage3_schema.py
mv ~/Desktop/stage4_refinement.py pipeline/stage4_refinement.py
mv ~/Desktop/repair.py validation/repair.py
git add .
git commit -m "Bulletproof pipeline with fallbacks - never fails"
git push origin main
cd ~/Desktop/compileros
mv ~/Desktop/stage1_intent.py pipeline/stage1_intent.py
mv ~/Desktop/stage2_architecture.py pipeline/stage2_architecture.py
mv ~/Desktop/stage3_schema.py pipeline/stage3_schema.py
mv ~/Desktop/stage4_refinement.py pipeline/stage4_refinement.py
mv ~/Desktop/repair.py validation/repair.py
git add .
git commit -m "Add keyword fallbacks to all stages - never fails"
git push origin main
cd ~/Desktop/compileros
mv ~/Desktop/stage1_intent.py pipeline/stage1_intent.py
mv ~/Desktop/stage2_architecture.py pipeline/stage2_architecture.py
mv ~/Desktop/stage3_schema.py pipeline/stage3_schema.py
mv ~/Desktop/stage4_refinement.py pipeline/stage4_refinement.py
mv ~/Desktop/repair.py validation/repair.py
git add .
git commit -m "Pure Python pipeline - no LLM JSON parsing"
git push origin main
cd ~/Desktop/compileros
source ~/.zshrc

sed -i '' 's/    # Try LLM for app_name/    # Skip LLM - use keyword extraction for app name/' pipeline/stage1_intent.py

cat > /tmp/fix_stage1.py << 'EOF'
content = open("pipeline/stage1_intent.py").read()

old = """    # Skip LLM - use keyword extraction for app name
    app_name = "App"
    try:
        resp = call_llm(f"What is a short 2-word name for this app: {user_input}. Reply with ONLY the name, nothing else.")
        name = resp.strip().split("\\n")[0][:30]
        if name and len(name) > 1:
            app_name = name
    except Exception:
        pass"""

new = """    # Extract app name from keywords
    app_name = "App"
    words_list = user_input.split()
    for i, w in enumerate(words_list):
        if w.lower() in ["crm", "lms", "erp", "cms"]:
            app_name = w.upper()
            break
        if w[0].isupper() and len(w) > 3:
            app_name = w
            break
    if app_name == "App" and words_list:
        app_name = words_list[0].title()"""

content = content.replace(old, new)
open("pipeline/stage1_intent.py", "w").write(content)
print("Fixed")
