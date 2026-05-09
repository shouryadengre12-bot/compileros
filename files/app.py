import streamlit as st
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_pipeline

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CompilerOS",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stage-box {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .success-badge {
        background: #a6e3a1;
        color: #1e1e2e;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .error-badge {
        background: #f38ba8;
        color: #1e1e2e;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .metric-card {
        background: #181825;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 0.75rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ CompilerOS")
    st.caption("Natural Language → Executable App Schema")
    st.divider()
    st.markdown("### How it works")
    st.markdown("""
    1. **Stage 1** — Extract Intent
    2. **Stage 2** — Design Architecture  
    3. **Stage 3** — Generate Schema
    4. **Stage 4** — Refine & Validate
    5. **Repair** — Auto-fix if needed
    """)
    st.divider()
    st.markdown("### Example prompts")
    examples = [
        "Build a CRM with login, contacts, dashboard, and role-based access for admins and sales reps",
        "Create an e-commerce store with product catalog, cart, and Stripe payments",
        "Build a project management tool with boards, tasks, and team collaboration",
    ]
    for ex in examples:
        if st.button(ex[:50] + "...", use_container_width=True):
            st.session_state["prefill"] = ex

# ── Main ─────────────────────────────────────────────────────────────────────
st.title("⚙️ CompilerOS")
st.caption("A multi-stage compiler: natural language → validated, executable app configuration")

# Input
prefill = st.session_state.get("prefill", "")
user_input = st.text_area(
    "Describe the app you want to build",
    value=prefill,
    height=120,
    placeholder="e.g. Build a CRM with login, contacts, dashboard, role-based access for admin and sales reps, and Stripe payments"
)

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("▶ Compile", type="primary", use_container_width=True)

if run_btn and user_input.strip():
    st.divider()
    
    # Stage status display
    stage_cols = st.columns(4)
    stage_labels = ["1. Intent", "2. Architecture", "3. Schema", "4. Refinement"]
    stage_placeholders = [col.empty() for col in stage_cols]
    
    for i, (ph, label) in enumerate(zip(stage_placeholders, stage_labels)):
        ph.markdown(f"⏳ **{label}**")

    result_placeholder = st.empty()
    progress = st.progress(0)
    status = st.empty()

    # ── Run pipeline with live stage updates ────────────────────────────────
    import threading
    import queue

    # We'll capture stdout stage prints and show progress
    # Run pipeline stages manually here for live UI feedback

    from pipeline.stage1_intent import extract_intent
    from pipeline.stage2_architecture import design_architecture
    from pipeline.stage3_schema import generate_schema
    from pipeline.stage4_refinement import refine_schema
    from validation.validator import validate_schema
    from validation.repair import repair_schema

    result = {
        "input": user_input,
        "stages": {},
        "final_schema": None,
        "validation": {"errors": [], "passed": False},
        "repair": {"attempted": False, "success": False},
        "metadata": {}
    }

    total_tokens_in = 0
    total_tokens_out = 0
    total_cost = 0
    pipeline_start = time.time()

    try:
        # Stage 1
        stage_placeholders[0].markdown("⚙️ **1. Intent**")
        status.info("Extracting intent from your description...")
        t0 = time.time()
        intent = extract_intent(user_input)
        s1_lat = (time.time() - t0) * 1000
        total_tokens_in += intent["_meta"]["input_tokens"]
        total_tokens_out += intent["_meta"]["output_tokens"]
        total_cost += intent["_meta"]["input_tokens"] * 0.000003 + intent["_meta"]["output_tokens"] * 0.000015
        result["stages"]["intent"] = {k: v for k, v in intent.items() if not k.startswith("_")}
        stage_placeholders[0].markdown(f"✅ **1. Intent** `{s1_lat:.0f}ms`")
        progress.progress(25)

        # Stage 2
        stage_placeholders[1].markdown("⚙️ **2. Architecture**")
        status.info("Designing system architecture...")
        t0 = time.time()
        architecture = design_architecture(intent)
        s2_lat = (time.time() - t0) * 1000
        total_tokens_in += architecture["_meta"]["input_tokens"]
        total_tokens_out += architecture["_meta"]["output_tokens"]
        total_cost += architecture["_meta"]["input_tokens"] * 0.000003 + architecture["_meta"]["output_tokens"] * 0.000015
        result["stages"]["architecture"] = {k: v for k, v in architecture.items() if not k.startswith("_")}
        stage_placeholders[1].markdown(f"✅ **2. Architecture** `{s2_lat:.0f}ms`")
        progress.progress(50)

        # Stage 3
        stage_placeholders[2].markdown("⚙️ **3. Schema**")
        status.info("Generating full UI, API, DB, and Auth schemas...")
        t0 = time.time()
        schema = generate_schema(architecture)
        s3_lat = (time.time() - t0) * 1000
        total_tokens_in += schema["_meta"]["input_tokens"]
        total_tokens_out += schema["_meta"]["output_tokens"]
        total_cost += schema["_meta"]["input_tokens"] * 0.000003 + schema["_meta"]["output_tokens"] * 0.000015
        stage_placeholders[2].markdown(f"✅ **3. Schema** `{s3_lat:.0f}ms`")
        progress.progress(75)

        # Stage 4
        stage_placeholders[3].markdown("⚙️ **4. Refinement**")
        status.info("Checking cross-layer consistency...")
        t0 = time.time()
        refined = refine_schema(schema)
        s4_lat = (time.time() - t0) * 1000
        total_tokens_in += refined["_meta"]["input_tokens"]
        total_tokens_out += refined["_meta"]["output_tokens"]
        total_cost += refined["_meta"]["input_tokens"] * 0.000003 + refined["_meta"]["output_tokens"] * 0.000015
        result["stages"]["refinements"] = refined.get("_refinements", [])
        stage_placeholders[3].markdown(f"✅ **4. Refinement** `{s4_lat:.0f}ms`")
        progress.progress(90)

        # Validation
        status.info("Validating schema...")
        is_valid, errors = validate_schema(refined)
        result["validation"]["errors"] = errors
        result["validation"]["passed"] = is_valid

        if not is_valid:
            status.warning(f"Found {len(errors)} issues — running repair engine...")
            repaired = repair_schema(refined, errors)
            is_valid2, errors2 = validate_schema(repaired)
            result["repair"]["attempted"] = True
            result["repair"]["success"] = is_valid2
            result["repair"]["changes"] = repaired.get("_meta", {}).get("errors_fixed", [])
            final = repaired
        else:
            final = refined

        result["final_schema"] = {k: v for k, v in final.items() if not k.startswith("_")}
        
        total_latency = (time.time() - pipeline_start) * 1000
        result["metadata"] = {
            "total_latency_ms": round(total_latency),
            "total_input_tokens": total_tokens_in,
            "total_output_tokens": total_tokens_out,
            "estimated_cost_usd": round(total_cost, 4),
            "success": is_valid or result["repair"]["success"]
        }
        progress.progress(100)
        status.success("✅ Compilation complete!")

    except Exception as e:
        status.error(f"Pipeline error: {e}")
        result["metadata"]["error"] = str(e)

    # ── Display Results ──────────────────────────────────────────────────────
    st.divider()

    # Metrics row
    m = result["metadata"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Status", "✅ Pass" if m.get("success") else "⚠️ Partial")
    c2.metric("Total Time", f"{m.get('total_latency_ms', 0):.0f}ms")
    c3.metric("Input Tokens", f"{m.get('total_input_tokens', 0):,}")
    c4.metric("Output Tokens", f"{m.get('total_output_tokens', 0):,}")
    c5.metric("Est. Cost", f"${m.get('estimated_cost_usd', 0):.4f}")

    st.divider()

    # Tabs for each layer
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Intent", "🏗️ Architecture", "🖥️ UI Schema",
        "🔌 API Schema", "🗄️ DB Schema", "🔐 Auth Schema"
    ])

    with tab1:
        st.subheader("Extracted Intent")
        intent_data = result["stages"].get("intent", {})
        if intent_data:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**App Name:** {intent_data.get('app_name', 'N/A')}")
                st.markdown(f"**App Type:** {intent_data.get('app_type', 'N/A')}")
                st.markdown(f"**Auth Required:** {'Yes' if intent_data.get('auth_required') else 'No'}")
                st.markdown(f"**Payments:** {'Yes' if intent_data.get('payment_required') else 'No'}")
            with col2:
                st.markdown("**Entities:**")
                for e in intent_data.get("entities", []):
                    st.markdown(f"  - {e}")
                st.markdown("**Roles:**")
                for r in intent_data.get("roles", []):
                    st.markdown(f"  - {r}")
            if intent_data.get("assumptions"):
                st.info("📝 **Assumptions made:** " + " | ".join(intent_data["assumptions"]))
            if intent_data.get("ambiguities"):
                st.warning("⚠️ **Ambiguities detected:** " + " | ".join(intent_data["ambiguities"]))

    with tab2:
        st.subheader("System Architecture")
        arch_data = result["stages"].get("architecture", {})
        if arch_data:
            st.markdown(f"**Pages:** {len(arch_data.get('pages', []))} | **Endpoints:** {len(arch_data.get('api_endpoints', []))} | **Entities:** {len(arch_data.get('entities', []))}")
        st.json(arch_data)
        refinements = result["stages"].get("refinements", [])
        if refinements:
            st.success("**Refinements applied:**\n" + "\n".join(f"• {r}" for r in refinements))

    final = result.get("final_schema") or {}

    with tab3:
        st.subheader("UI Schema")
        st.json(final.get("ui_schema", {}) if final else {})

    with tab4:
        st.subheader("API Schema")
        st.json(final.get("api_schema", {}) if final else {})

    with tab5:
        st.subheader("Database Schema")
        st.json(final.get("db_schema", {}) if final else {})

    with tab6:
        st.subheader("Auth Schema")
        st.json(final.get("auth_schema", {}) if final else {})

    # Validation status
    st.divider()
    with st.expander("🔍 Validation & Repair Details"):
        v = result["validation"]
        if v["passed"]:
            st.success("✅ All validation checks passed")
        else:
            st.error(f"❌ {len(v['errors'])} validation errors found")
            for err in v["errors"]:
                st.code(err)

        r = result["repair"]
        if r["attempted"]:
            if r["success"]:
                st.success("🔧 Repair engine fixed all issues")
            else:
                st.warning("🔧 Repair engine partially fixed issues")
            if r.get("changes"):
                st.markdown("**Changes made:**")
                for ch in r["changes"]:
                    st.markdown(f"  - {ch}")

    # Full JSON download
    st.download_button(
        "⬇️ Download Full Schema JSON",
        data=json.dumps(result["final_schema"], indent=2),
        file_name="compileros_schema.json",
        mime="application/json"
    )

elif run_btn:
    st.warning("Please enter an app description first.")
