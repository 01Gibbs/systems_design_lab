"""Fixed Latency Scenario"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class FixedLatency:
    """Adds fixed latency to HTTP routes"""

    meta = ScenarioMeta(
        name="fixed-latency",
        description="Adds fixed latency (ms) to matching HTTP routes.",
        targets=["http"],
        parameter_schema={
            "type": "object",
            "properties": {
                "ms": {"type": "integer", "minimum": 1, "maximum": 10_000},
                "path_prefix": {"type": "string"},
                "method": {"type": "string"},
                "probability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            },
            "required": ["ms"],
        },
        safety_limits={"max_ms": 10_000},
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "http"

    def apply(self, *, ctx: dict, parameters: dict) -> dict:
        """Returns effect dict - NO side effects here"""
        p = float(parameters.get("probability", 1.0))
        if random.random() > p:
            return {}

        return {
            "http_delay_ms": int(parameters["ms"]),
            "http_path_prefix": str(parameters.get("path_prefix", "")),
            "http_method": str(parameters.get("method", "")).upper(),
        }
