import streamlit as st
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.stage1_intent import extract_intent
from pipeline.stage2_architecture import design_architecture
from pipeline.stage3_schema import generate_schema
from pipeline.stage4_refinement import refine_schema
from validation.validator import validate_schema
from validation.repair import repair_schema

st.set_page_config(page_title="CompilerOS", page_icon="⚙️", layout="wide")

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
        if st.button(ex[:50] + "...", use_container_width=True):
            st.session_state["prefill"] = ex

st.title("⚙️ CompilerOS")
st.caption("A multi-stage compiler: natural language → validated, executable app configuration")

prefill = st.session_state.get("prefill", "")
user_input = st.text_area("Describe the app you want to build", value=prefill, height=120,
    placeholder="e.g. Build a CRM with login, contacts, dashboard, role-based access for admin and sales reps")

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("▶ Compile", type="primary", use_container_width=True)

if run_btn and user_input.strip():
    st.divider()
    stage_cols = st.columns(4)
    stage_labels = ["1. Intent", "2. Architecture", "3. Schema", "4. Refinement"]
    stage_placeholders = [col.empty() for col in stage_cols]
    for ph, label in zip(stage_placeholders, stage_labels):
        ph.markdown(f"⏳ **{label}**")

    progress = st.progress(0)
    status = st.empty()
    result = {"stages": {}, "final_schema": {}, "validation": {"errors": [], "passed": False}, "repair": {"attempted": False, "success": False}, "metadata": {}}
    pipeline_start = time.time()

    try:
        stage_placeholders[0].markdown("⚙️ **1. Intent**")
        status.info("Extracting intent...")
        t0 = time.time()
        intent = extract_intent(user_input)
        if not isinstance(intent, dict):
            intent = {}
        result["stages"]["intent"] = {k: v for k, v in intent.items() if not k.startswith("_")}
        stage_placeholders[0].markdown(f"✅ **1. Intent** `{(time.time()-t0)*1000:.0f}ms`")
        progress.progress(25)

        stage_placeholders[1].markdown("⚙️ **2. Architecture**")
        status.info("Designing architecture...")
        t0 = time.time()
        architecture = design_architecture(intent)
        if not isinstance(architecture, dict):
            architecture = {}
        result["stages"]["architecture"] = {k: v for k, v in architecture.items() if not k.startswith("_")}
        stage_placeholders[1].markdown(f"✅ **2. Architecture** `{(time.time()-t0)*1000:.0f}ms`")
        progress.progress(50)

        stage_placeholders[2].markdown("⚙️ **3. Schema**")
        status.info("Generating schemas...")
        t0 = time.time()
        schema = generate_schema(architecture)
        if not isinstance(schema, dict):
            schema = {}
        stage_placeholders[2].markdown(f"✅ **3. Schema** `{(time.time()-t0)*1000:.0f}ms`")
        progress.progress(75)

        stage_placeholders[3].markdown("⚙️ **4. Refinement**")
        status.info("Refining...")
        t0 = time.time()
        try:
            refined = refine_schema(schema)
            if not isinstance(refined, dict):
                refined = schema
        except Exception:
            refined = schema
        result["stages"]["refinements"] = refined.get("_refinements", []) if isinstance(refined, dict) else []
        stage_placeholders[3].markdown(f"✅ **4. Refinement** `{(time.time()-t0)*1000:.0f}ms`")
        progress.progress(90)

        status.info("Validating...")
        is_valid, errors = validate_schema(refined)
        result["validation"]["errors"] = errors
        result["validation"]["passed"] = is_valid

        if not is_valid:
            repaired = repair_schema(refined, errors)
            if not isinstance(repaired, dict):
                repaired = refined
            is_valid2, _ = validate_schema(repaired)
            result["repair"]["attempted"] = True
            result["repair"]["success"] = is_valid2
            final = repaired
        else:
            final = refined

        if not isinstance(final, dict):
            final = {}
        result["final_schema"] = {k: v for k, v in final.items() if not k.startswith("_")}
        total_latency = (time.time()-pipeline_start)*1000
        result["metadata"] = {"total_latency_ms": round(total_latency), "total_input_tokens": 0, "total_output_tokens": 0, "estimated_cost_usd": 0, "success": is_valid or result["repair"].get("success", False)}
        progress.progress(100)
        status.success("✅ Compilation complete!")

    except Exception as e:
        status.error(f"Pipeline error: {e}")
        result["metadata"]["error"] = str(e)

    st.divider()
    m = result.get("metadata", {})
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Status", "✅ Pass" if m.get("success") else "⚠️ Partial")
    c2.metric("Total Time", f"{m.get('total_latency_ms', 0):.0f}ms")
    c3.metric("Input Tokens", f"{m.get('total_input_tokens', 0):,}")
    c4.metric("Output Tokens", f"{m.get('total_output_tokens', 0):,}")
    c5.metric("Est. Cost", f"${m.get('estimated_cost_usd', 0):.4f}")

    st.divider()
    final = result.get("final_schema") or {}
    if not isinstance(final, dict):
        final = {}

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Intent", "🏗️ Architecture", "🖥️ UI Schema", "🔌 API Schema", "🗄️ DB Schema", "🔐 Auth Schema"])

    with tab1:
        st.subheader("Extracted Intent")
        intent_data = result["stages"].get("intent", {})
        if isinstance(intent_data, dict) and intent_data:
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
                st.info("📝 **Assumptions:** " + " | ".join(intent_data["assumptions"]))

    with tab2:
        st.subheader("System Architecture")
        arch_data = result["stages"].get("architecture", {})
        st.json(arch_data if isinstance(arch_data, dict) else {})

    with tab3:
        st.subheader("UI Schema")
        st.json(final.get("ui_schema", {}) if isinstance(final, dict) else {})

    with tab4:
        st.subheader("API Schema")
        st.json(final.get("api_schema", {}) if isinstance(final, dict) else {})

    with tab5:
        st.subheader("Database Schema")
        st.json(final.get("db_schema", {}) if isinstance(final, dict) else {})

    with tab6:
        st.subheader("Auth Schema")
        st.json(final.get("auth_schema", {}) if isinstance(final, dict) else {})

    st.divider()
    with st.expander("🔍 Validation & Repair Details"):
        v = result.get("validation", {})
        if v.get("passed"):
            st.success("✅ All validation checks passed")
        else:
            st.error(f"❌ {len(v.get('errors', []))} validation errors found")
            for err in v.get("errors", []):
                st.code(err)
        r = result.get("repair", {})
        if r.get("attempted"):
            st.success("🔧 Repair engine ran") if r.get("success") else st.warning("🔧 Repair attempted")

    st.download_button("⬇️ Download Full Schema JSON",
        data=json.dumps(result.get("final_schema", {}), indent=2),
        file_name="compileros_schema.json", mime="application/json")

elif run_btn:
    st.warning("Please enter an app description first.")
