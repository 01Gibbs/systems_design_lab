"""Algorithmic Degradation Scenario"""

from __future__ import annotations

from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class AlgorithmicDegradation:
    """Toggle between O(n) and O(n²) algorithms"""

    meta = ScenarioMeta(
        name="algorithmic-degradation",
        description="Toggle O(n) vs O(n²) algorithm implementations.",
        targets=["algorithm", "cpu"],
        parameter_schema={
            "type": "object",
            "properties": {
                "use_slow_path": {"type": "boolean"},
                "input_size": {"type": "integer", "minimum": 1, "maximum": 10_000},
            },
            "required": ["use_slow_path"],
        },
        safety_limits={"max_input_size": 10_000},
        metrics=[
            MetricSpec(
                name="algorithm_operations_total",
                type="counter",
                description="Total number of algorithm operations by scenario and complexity",
                labels=["scenario", "complexity"],
            ),
            MetricSpec(
                name="algorithm_complexity",
                type="gauge",
                description="Current algorithmic complexity (1=O(n), 2=O(n^2))",
                labels=["scenario"],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        cat = target.get("category")
        return cat in ("algorithm", "cpu")

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict - NO side effects here"""
        use_slow_path = parameters["use_slow_path"]
        input_size = parameters.get("input_size", 100)
        return {
            "algorithm_use_slow": bool(use_slow_path),
            "algorithm_input_size": int(input_size) if isinstance(input_size, (int, str)) else 100,
        }
