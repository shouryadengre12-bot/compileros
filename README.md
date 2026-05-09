# ⚙️ CompilerOS

**Natural Language → Validated, Executable App Configuration**

A multi-stage compiler that converts plain English app descriptions into structured, cross-validated JSON schemas ready to power real applications.

---

## What It Does

You type:
> "Build a CRM with login, contacts, dashboard, role-based access for admin and sales reps, and Stripe payments"

It outputs a complete, validated JSON schema with:
- **UI Schema** — pages, components, layouts, role access
- **API Schema** — endpoints, methods, auth, request/response shapes
- **DB Schema** — tables, columns, types, indexes, relations
- **Auth Schema** — roles, permissions, protected routes, JWT config

---

## Live Demo

🔗 **[https://compileros-v8fqfgf7ypyd8rwhlbftkl.streamlit.app/](https://compileros-v8fqfgf7ypyd8rwhlbftkl.streamlit.app/)**

---

## Architecture

```
User Prompt
    │
    ▼
┌─────────────────────────────────┐
│  Stage 1: Intent Extraction     │  → entities, roles, features, assumptions
│  (separate LLM call)            │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  Stage 2: Architecture Design   │  → pages, API endpoints, entity relations
│  (separate LLM call)            │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  Stage 3: Schema Generation     │  → full UI/API/DB/Auth JSON schemas
│  (separate LLM call)            │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  Stage 4: Refinement            │  → cross-layer consistency fixes
│  (separate LLM call)            │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  Validation Engine (no LLM)     │  → 7 structural + cross-layer checks
└──────────────┬──────────────────┘
         (if errors)
               ▼
┌─────────────────────────────────┐
│  Targeted Repair Engine         │  → fixes specific layers only
│  (separate LLM call)            │     NOT a full retry
└──────────────┬──────────────────┘
               ▼
      Final Validated JSON Schema
```

Each stage is a **separate LLM call** with a targeted prompt — not a single mega-prompt.

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/shouryadengre12-bot/compileros.git
cd compileros
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free API key
- Go to **openrouter.ai**
- Sign up → Create API key (free)
- Copy the key

### 5. Set your API key
```bash
export OPENROUTER_API_KEY=your_key_here
```

### 6. Run the web UI
```bash
streamlit run app.py
```

### 7. Run from command line
```bash
python main.py
```

### 8. Run full evaluation (20 test cases)
```bash
python run_eval.py --subset all
python run_eval.py --subset real
python run_eval.py --subset edge
```

---

## Output Schema Structure

```json
{
  "ui_schema": {
    "pages": [
      {
        "id": "dashboard",
        "name": "Dashboard",
        "route": "/dashboard",
        "layout": "sidebar",
        "components": [...],
        "roles_allowed": ["admin", "sales_rep"]
      }
    ]
  },
  "api_schema": {
    "base_url": "/api/v1",
    "endpoints": [
      {
        "id": "get_contacts",
        "method": "GET",
        "path": "/api/v1/contacts",
        "auth_required": true,
        "roles": ["admin", "sales_rep"],
        "request_schema": {},
        "response_schema": {"contacts": {"type": "array"}},
        "db_table": "contacts"
      }
    ]
  },
  "db_schema": {
    "tables": [
      {
        "name": "contacts",
        "columns": [
          {"name": "id", "type": "INT", "primary_key": true},
          {"name": "name", "type": "VARCHAR", "nullable": false},
          {"name": "email", "type": "VARCHAR", "unique": true},
          {"name": "created_at", "type": "TIMESTAMP"}
        ]
      }
    ]
  },
  "auth_schema": {
    "strategy": "JWT",
    "token_expiry": "24h",
    "roles": [
      {"name": "admin", "permissions": ["contacts:read", "contacts:write", "analytics:read"]},
      {"name": "sales_rep", "permissions": ["contacts:read", "contacts:write"]}
    ],
    "protected_routes": [
      {"route": "/dashboard", "roles": ["admin", "sales_rep"]},
      {"route": "/analytics", "roles": ["admin"]}
    ]
  }
}
```

---

## Validation Engine — 7 Checks

1. All 4 top-level keys present (`ui_schema`, `api_schema`, `db_schema`, `auth_schema`)
2. Pages have required fields (`id`, `name`, `route`, `components`)
3. API endpoints have required fields (`method`, `path`, `auth_required`)
4. DB tables have required fields + `id` column
5. Auth schema has `roles` + `strategy`
6. **Cross-layer:** API `db_table` references must exist in DB schema
7. **Cross-layer:** UI `data_source` references must match API paths

---

## Repair Engine

Targeted repair — not blind retry:
- Categorizes errors by layer (`UI_ERROR`, `API_ERROR`, `DB_ERROR`, `AUTH_ERROR`, `CROSS_LAYER`)
- Sends only broken schema + specific errors to LLM
- Fixes only what is broken
- Re-validates after repair
- Max 3 attempts before returning best-effort output

---

## Failure Handling

- **Vague prompts** — makes reasonable assumptions and documents them
- **Conflicting requirements** — detects and resolves with standard patterns
- **Incomplete specs** — infers missing parts based on app type
- **Overspecified prompts** — handles full complexity across all layers

---

## Evaluation Dataset

**10 real product prompts:**
CRM, E-commerce, Project Management, Healthcare, LMS, HR Management, Real Estate, Food Delivery, SaaS Analytics, Social Network

**10 edge cases:**
- Vague: "Build an app for my business"
- Conflicting: "All users are admins but admins have special access"
- Incomplete: "Build a marketplace"
- Overspecified: todo app with 12+ features
- No-auth: public blog with no login
- Single feature: contact form only
- Ambiguous roles: doctors, patients, pharmacies, insurance
- And more

**Metrics tracked:** success rate, repair attempts, failure types, latency per stage, estimated cost

---

## Cost & Latency

| Scenario | Avg Latency | Cost |
|---|---|---|
| Simple app | ~10-15s | $0.00 (free tier) |
| Complex app | ~20-30s | $0.00 (free tier) |
| With repair | ~35-45s | $0.00 (free tier) |

Model: `liquid/lfm-2.5-1.2b-instruct:free` via OpenRouter
4 LLM calls per compilation + 1 repair call if needed.

---

## Key Design Decisions

**Why multi-stage?**
Each stage has one focused job. This reduces hallucination, makes outputs predictable, and makes failures debuggable — you can see exactly which stage failed and why.

**Why targeted repair vs full retry?**
Full retry wastes tokens and can introduce new errors. Targeted repair sends only the broken parts + specific error list so the LLM fixes exactly what is wrong.

**Why OpenRouter free tier?**
Zero cost, reliable uptime, access to multiple free models. Falls back gracefully if one model is rate-limited.

**Why Streamlit?**
Evaluators can see each pipeline stage run live — making the multi-stage architecture visible and verifiable rather than a black box.

---

## File Structure

```
compileros/
├── pipeline/
│   ├── __init__.py
│   ├── stage1_intent.py        # Stage 1: Intent extraction
│   ├── stage2_architecture.py  # Stage 2: System design
│   ├── stage3_schema.py        # Stage 3: Full schema generation
│   └── stage4_refinement.py    # Stage 4: Cross-layer refinement
├── validation/
│   ├── __init__.py
│   ├── validator.py            # 7-check validation engine (no LLM)
│   └── repair.py               # Targeted repair engine
├── evaluation/
│   ├── __init__.py
│   ├── test_cases.py           # 20 test prompts (10 real + 10 edge)
│   └── metrics.py              # Metrics tracking & reporting
├── main.py                     # Pipeline orchestrator (CLI)
├── app.py                      # Streamlit web UI
├── run_eval.py                 # Evaluation runner
├── requirements.txt
└── README.md
```
