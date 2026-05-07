import time
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.stage1_intent import extract_intent
from pipeline.stage2_architecture import design_architecture
from pipeline.stage3_schema import generate_schema
from pipeline.stage4_refinement import refine_schema
from validation.validator import validate_schema
from validation.repair import repair_schema
from evaluation.metrics import CompilationMetric, StageMetric, MetricsTracker


def run_pipeline(user_input: str, test_id: str = "manual", category: str = "manual") -> dict:
    """
    Full 4-stage compilation pipeline.
    Returns the final validated schema + pipeline metadata.
    """
    metric = CompilationMetric(test_id=test_id, prompt=user_input, category=category)
    pipeline_start = time.time()
    
    output = {
        "input": user_input,
        "stages": {},
        "final_schema": None,
        "validation": {"errors": [], "passed": False},
        "repair": {"attempted": False, "success": False, "changes": []},
        "metadata": {}
    }

    # ── STAGE 1: Intent Extraction ──────────────────────────────────────────
    print("⚙️  Stage 1: Extracting intent...")
    t0 = time.time()
    try:
        intent = extract_intent(user_input)
        latency = (time.time() - t0) * 1000
        output["stages"]["intent"] = intent
        metric.add_stage(StageMetric(
            stage="intent",
            success=True,
            latency_ms=latency,
            input_tokens=intent["_meta"]["input_tokens"],
            output_tokens=intent["_meta"]["output_tokens"]
        ))
        print(f"   ✅ Intent extracted ({latency:.0f}ms)")
        if intent.get("ambiguities"):
            print(f"   ⚠️  Ambiguities detected: {intent['ambiguities']}")
        if intent.get("assumptions"):
            print(f"   📝 Assumptions: {intent['assumptions']}")
    except Exception as e:
        print(f"   ❌ Stage 1 failed: {e}")
        metric.add_stage(StageMetric(stage="intent", success=False, latency_ms=(time.time()-t0)*1000, error=str(e)))
        output["metadata"]["error"] = f"Stage 1 failed: {e}"
        return output

    # ── STAGE 2: Architecture Design ────────────────────────────────────────
    print("⚙️  Stage 2: Designing architecture...")
    t0 = time.time()
    try:
        architecture = design_architecture(intent)
        latency = (time.time() - t0) * 1000
        output["stages"]["architecture"] = architecture
        metric.add_stage(StageMetric(
            stage="architecture",
            success=True,
            latency_ms=latency,
            input_tokens=architecture["_meta"]["input_tokens"],
            output_tokens=architecture["_meta"]["output_tokens"]
        ))
        print(f"   ✅ Architecture designed ({latency:.0f}ms)")
    except Exception as e:
        print(f"   ❌ Stage 2 failed: {e}")
        metric.add_stage(StageMetric(stage="architecture", success=False, latency_ms=(time.time()-t0)*1000, error=str(e)))
        output["metadata"]["error"] = f"Stage 2 failed: {e}"
        return output

    # ── STAGE 3: Schema Generation ──────────────────────────────────────────
    print("⚙️  Stage 3: Generating full schema...")
    t0 = time.time()
    try:
        schema = generate_schema(architecture)
        latency = (time.time() - t0) * 1000
        metric.add_stage(StageMetric(
            stage="schema",
            success=True,
            latency_ms=latency,
            input_tokens=schema["_meta"]["input_tokens"],
            output_tokens=schema["_meta"]["output_tokens"]
        ))
        print(f"   ✅ Schema generated ({latency:.0f}ms)")
    except Exception as e:
        print(f"   ❌ Stage 3 failed: {e}")
        metric.add_stage(StageMetric(stage="schema", success=False, latency_ms=(time.time()-t0)*1000, error=str(e)))
        output["metadata"]["error"] = f"Stage 3 failed: {e}"
        return output

    # ── STAGE 4: Refinement ─────────────────────────────────────────────────
    print("⚙️  Stage 4: Refining cross-layer consistency...")
    t0 = time.time()
    try:
        refined = refine_schema(schema)
        latency = (time.time() - t0) * 1000
        output["stages"]["refinement"] = refined.get("_refinements", [])
        metric.add_stage(StageMetric(
            stage="refinement",
            success=True,
            latency_ms=latency,
            input_tokens=refined["_meta"]["input_tokens"],
            output_tokens=refined["_meta"]["output_tokens"]
        ))
        print(f"   ✅ Schema refined ({latency:.0f}ms)")
        if refined.get("_refinements"):
            for r in refined["_refinements"]:
                print(f"      → {r}")
    except Exception as e:
        print(f"   ⚠️  Stage 4 failed (using unrefined schema): {e}")
        refined = schema

    # ── VALIDATION ──────────────────────────────────────────────────────────
    print("🔍 Validating schema...")
    is_valid, errors = validate_schema(refined)
    output["validation"]["errors"] = errors
    output["validation"]["passed"] = is_valid
    metric.validation_errors = errors

    if is_valid:
        print(f"   ✅ Validation passed")
        output["final_schema"] = {k: v for k, v in refined.items() if not k.startswith("_")}
    else:
        print(f"   ⚠️  {len(errors)} validation error(s) found:")
        for e in errors:
            print(f"      - {e}")

        # ── REPAIR ──────────────────────────────────────────────────────────
        print("🔧 Running targeted repair...")
        metric.repair_attempted = True
        output["repair"]["attempted"] = True

        t0 = time.time()
        repaired = repair_schema(refined, errors)
        repair_latency = (time.time() - t0) * 1000

        is_valid_after, errors_after = validate_schema(repaired)

        if is_valid_after:
            print(f"   ✅ Repair successful ({repair_latency:.0f}ms)")
            metric.repair_success = True
            output["repair"]["success"] = True
            output["repair"]["changes"] = repaired.get("_meta", {}).get("errors_fixed", [])
            output["final_schema"] = {k: v for k, v in repaired.items() if not k.startswith("_")}
        else:
            print(f"   ❌ Repair could not fix all errors. Remaining: {errors_after}")
            output["repair"]["success"] = False
            output["repair"]["remaining_errors"] = errors_after
            # Still return best-effort schema
            output["final_schema"] = {k: v for k, v in repaired.items() if not k.startswith("_")}

    # ── METADATA ────────────────────────────────────────────────────────────
    total_latency = (time.time() - pipeline_start) * 1000
    metric.total_latency_ms = total_latency
    metric.final_success = output["validation"]["passed"] or output["repair"].get("success", False)

    output["metadata"] = {
        "total_latency_ms": round(total_latency, 0),
        "total_input_tokens": metric.total_input_tokens,
        "total_output_tokens": metric.total_output_tokens,
        "estimated_cost_usd": round(metric.estimated_cost_usd, 4),
        "stages_completed": len([s for s in output["stages"]]),
        "success": metric.final_success
    }

    print(f"\n{'✅' if metric.final_success else '⚠️'} Pipeline complete | {total_latency:.0f}ms | ~${metric.estimated_cost_usd:.4f}")
    return output


if __name__ == "__main__":
    prompt = input("Enter your app description: ").strip()
    if not prompt:
        prompt = "Build a CRM with login, contacts, dashboard, role-based access for admin and sales reps, and Stripe payments."

    result = run_pipeline(prompt)
    print("\n" + "="*60)
    print("FINAL OUTPUT:")
    print("="*60)
    print(json.dumps(result["final_schema"], indent=2))
    print("\nMETADATA:", json.dumps(result["metadata"], indent=2))
