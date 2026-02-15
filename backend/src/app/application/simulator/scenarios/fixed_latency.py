"""Fixed Latency Scenario"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


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
        metrics=[
            MetricSpec(
                name="http_injected_latency_seconds",
                type="histogram",
                description="Injected HTTP latency (seconds) by scenario and endpoint",
                labels=["scenario", "endpoint"],
                buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5],
            ),
            MetricSpec(
                name="http_latency_injections_total",
                type="counter",
                description="Total number of HTTP latency injections by scenario and endpoint",
                labels=["scenario", "endpoint"],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "http"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict - NO side effects here"""
        prob = parameters.get("probability", 1.0)
        p = float(prob) if isinstance(prob, (int, float, str)) else 1.0
        if random.random() > p:
            return {}

        ms = parameters["ms"]
        return {
            "http_delay_ms": int(ms) if isinstance(ms, (int, str)) else 0,
            "http_path_prefix": str(parameters.get("path_prefix", "")),
            "http_method": str(parameters.get("method", "")).upper(),
            "scenario_name": self.meta.name,
        }
