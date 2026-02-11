"""Algorithmic Degradation Scenario"""

from __future__ import annotations

from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


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
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        cat = target.get("category")
        return cat in ("algorithm", "cpu")

    def apply(self, *, ctx: dict, parameters: dict) -> dict:
        """Returns effect dict - NO side effects here"""
        return {
            "algorithm_use_slow": bool(parameters["use_slow_path"]),
            "algorithm_input_size": int(parameters.get("input_size", 100)),
        }
