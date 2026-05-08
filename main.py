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


def ensure_dict(obj, stage_name):
    """Make sure output is always a dict."""
    if isinstance(obj, str):
        try:
            from json_repair import repair_json
            parsed = repair_json(obj)
            if isinstance(parsed, str):
                return json.loads(parsed)
            return parsed
        except Exception as e:
            raise ValueError(f"Stage {stage_name} returned a string instead of dict: {obj[:200]}")
    if not isinstance(obj, dict):
        raise ValueError(f"Stage {stage_name} returned {type(obj)} instead of dict")
    return obj


def run_pipeline(user_input: str, test_id: str = "manual", category: str = "manual") -> dict:
    pipeline_start = time.time()

    output = {
        "input": user_input,
        "stages": {},
        "final_schema": None,
        "validation": {"errors": [], "passed": False},
        "repair": {"attempted": False, "success": False},
        "metadata": {}
    }

    # Stage 1
    print("Stage 1: Extracting intent...")
    t0 = time.time()
    try:
        intent = extract_intent(user_input)
        intent = ensure_dict(intent, "1_intent")
        output["stages"]["intent"] = {k: v for k, v in intent.items() if not k.startswith("_")}
        print(f"   Done ({(time.time()-t0)*1000:.0f}ms)")
    except Exception as e:
        output["metadata"]["error"] = f"Stage 1 failed: {e}"
        return output

    # Stage 2
    print("Stage 2: Designing architecture...")
    t0 = time.time()
    try:
        architecture = design_architecture(intent)
        architecture = ensure_dict(architecture, "2_architecture")
        output["stages"]["architecture"] = {k: v for k, v in architecture.items() if not k.startswith("_")}
        print(f"   Done ({(time.time()-t0)*1000:.0f}ms)")
    except Exception as e:
        output["metadata"]["error"] = f"Stage 2 failed: {e}"
        return output

    # Stage 3
    print("Stage 3: Generating schema...")
    t0 = time.time()
    try:
        schema = generate_schema(architecture)
        schema = ensure_dict(schema, "3_schema")
        print(f"   Done ({(time.time()-t0)*1000:.0f}ms)")
    except Exception as e:
        output["metadata"]["error"] = f"Stage 3 failed: {e}"
        return output

    # Stage 4
    print("Stage 4: Refining...")
    t0 = time.time()
    try:
        refined = refine_schema(schema)
        refined = ensure_dict(refined, "4_refinement")
        output["stages"]["refinements"] = refined.get("_refinements", [])
        print(f"   Done ({(time.time()-t0)*1000:.0f}ms)")
    except Exception as e:
        refined = schema

    # Validation
    is_valid, errors = validate_schema(refined)
    output["validation"]["errors"] = errors
    output["validation"]["passed"] = is_valid

    if not is_valid:
        repaired = repair_schema(refined, errors)
        if isinstance(repaired, str):
            repaired = schema
        is_valid2, errors2 = validate_schema(repaired)
        output["repair"]["attempted"] = True
        output["repair"]["success"] = is_valid2
        final = repaired
    else:
        final = refined

    output["final_schema"] = {k: v for k, v in final.items() if not k.startswith("_")}

    total_latency = (time.time() - pipeline_start) * 1000
    output["metadata"] = {
        "total_latency_ms": round(total_latency),
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "estimated_cost_usd": 0,
        "success": is_valid or output["repair"].get("success", False)
    }

    return output


if __name__ == "__main__":
    prompt = input("Enter your app description: ").strip()
    if not prompt:
        prompt = "Build a CRM with login, contacts, dashboard, role-based access for admin and sales reps."
    result = run_pipeline(prompt)
    print(json.dumps(result["final_schema"], indent=2))
