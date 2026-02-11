"""Error Burst Scenario"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class ErrorBurst:
    """Returns 500 errors with probability p"""

    meta = ScenarioMeta(
        name="error-burst-5xx",
        description="Returns 500 errors with probability p on matching HTTP routes.",
        targets=["http"],
        parameter_schema={
            "type": "object",
            "properties": {
                "probability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "path_prefix": {"type": "string"},
                "method": {"type": "string"},
            },
            "required": ["probability"],
        },
        safety_limits={"max_probability": 1.0},
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "http"

        def apply(self, *, ctx: dict, parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict - NO side effects here"""
        p = float(parameters["probability"])
        if random.random() > p:
            return {}

        return {
            "http_force_error": True,
            "http_path_prefix": str(parameters.get("path_prefix", "")),
            "http_method": str(parameters.get("method", "")).upper(),
        }
