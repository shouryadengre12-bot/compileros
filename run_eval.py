"""
Run all 20 test cases and generate evaluation report.
Usage: python run_eval.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_pipeline
from evaluation.test_cases import ALL_TEST_CASES, REAL_PROMPTS, EDGE_CASES
from evaluation.metrics import MetricsTracker, CompilationMetric, StageMetric


def run_evaluation(subset=None, save_path="evaluation/results.json"):
    tracker = MetricsTracker()
    cases = subset or ALL_TEST_CASES

    print(f"\n{'='*60}")
    print(f"COMPILEROS EVALUATION — {len(cases)} test cases")
    print(f"{'='*60}\n")

    for i, case in enumerate(cases):
        print(f"\n[{i+1}/{len(cases)}] {case['id']} — {case['category']}")
        print(f"Prompt: {case['prompt'][:80]}...")
        print("-" * 40)

        start = time.time()
        result = run_pipeline(
            user_input=case["prompt"],
            test_id=case["id"],
            category=case["category"]
        )
        elapsed = time.time() - start

        # Build metric from result
        m = CompilationMetric(
            test_id=case["id"],
            prompt=case["prompt"],
            category=case["category"],
            total_latency_ms=result["metadata"].get("total_latency_ms", elapsed * 1000),
            validation_errors=result["validation"].get("errors", []),
            repair_attempted=result["repair"].get("attempted", False),
            repair_success=result["repair"].get("success", False),
            final_success=result["metadata"].get("success", False),
            total_input_tokens=result["metadata"].get("total_input_tokens", 0),
            total_output_tokens=result["metadata"].get("total_output_tokens", 0),
            estimated_cost_usd=result["metadata"].get("estimated_cost_usd", 0)
        )
        tracker.add(m)

        # Small delay to avoid rate limits
        time.sleep(2)

    # Save and print summary
    tracker.save(save_path)
    summary = tracker.summary()

    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    for k, v in summary.items():
        if k != "failure_type_breakdown":
            print(f"  {k}: {v}")
    print("\nFailure breakdown:")
    for ftype, count in summary.get("failure_type_breakdown", {}).items():
        print(f"  {ftype}: {count}")
    print(f"{'='*60}")

    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--subset", choices=["real", "edge", "all"], default="all")
    args = parser.parse_args()

    subset_map = {"real": REAL_PROMPTS, "edge": EDGE_CASES, "all": None}
    run_evaluation(subset=subset_map[args.subset])
