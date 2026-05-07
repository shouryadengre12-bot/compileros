import time
import json
from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class StageMetric:
    stage: str
    success: bool
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None


@dataclass
class CompilationMetric:
    test_id: str
    prompt: str
    category: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_latency_ms: float = 0
    stages: list = field(default_factory=list)
    validation_errors: list = field(default_factory=list)
    repair_attempted: bool = False
    repair_success: bool = False
    final_success: bool = False
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    estimated_cost_usd: float = 0

    def add_stage(self, metric: StageMetric):
        self.stages.append(asdict(metric))
        self.total_input_tokens += metric.input_tokens
        self.total_output_tokens += metric.output_tokens
        # Claude Sonnet pricing: ~$3/M input, $15/M output
        self.estimated_cost_usd += (
            metric.input_tokens * 0.000003 +
            metric.output_tokens * 0.000015
        )

    def to_dict(self):
        return asdict(self)


class MetricsTracker:
    def __init__(self):
        self.results = []

    def add(self, metric: CompilationMetric):
        self.results.append(metric)

    def summary(self) -> dict:
        if not self.results:
            return {}

        total = len(self.results)
        successes = sum(1 for r in self.results if r.final_success)
        repairs = sum(1 for r in self.results if r.repair_attempted)
        repair_successes = sum(1 for r in self.results if r.repair_success)

        avg_latency = sum(r.total_latency_ms for r in self.results) / total
        avg_cost = sum(r.estimated_cost_usd for r in self.results) / total

        # Failure type breakdown
        failure_types = {}
        for r in self.results:
            for err in r.validation_errors:
                prefix = err.split(":")[0]
                failure_types[prefix] = failure_types.get(prefix, 0) + 1

        return {
            "total_runs": total,
            "success_rate": f"{successes/total*100:.1f}%",
            "successes": successes,
            "failures": total - successes,
            "repair_attempts": repairs,
            "repair_success_rate": f"{repair_successes/repairs*100:.1f}%" if repairs > 0 else "N/A",
            "avg_latency_ms": round(avg_latency, 0),
            "avg_cost_usd": round(avg_cost, 4),
            "total_cost_usd": round(sum(r.estimated_cost_usd for r in self.results), 4),
            "failure_type_breakdown": failure_types
        }

    def save(self, path: str):
        data = {
            "summary": self.summary(),
            "results": [r.to_dict() for r in self.results]
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Metrics saved to {path}")
