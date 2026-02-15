"""Clock Skew Scenario - Simulates system clock drift/skew"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class ClockSkew:
    """Simulates system clock skew by shifting reported time"""

    meta = ScenarioMeta(
        name="clock-skew",
        description="Simulates system clock skew: shifts reported time for requests.",
        targets=["http", "db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "skew_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of clock skew event",
                },
                "skew_ms": {
                    "type": "integer",
                    "minimum": -60000,
                    "maximum": 60000,
                    "description": "Amount of clock skew in milliseconds (+/-)",
                },
            },
            "required": ["skew_probability"],
        },
        safety_limits={"max_skew_ms": 60000},
        metrics=[
            MetricSpec(
                name="clock_skew_seconds",
                type="gauge",
                description="System clock skew (seconds) by scenario",
                labels=["scenario"],
            ),
            MetricSpec(
                name="time_sync_failures_total",
                type="counter",
                description="Total time sync failures by scenario",
                labels=["scenario"],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") in ("http", "database", "time")

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        skew_probability = float(str(parameters["skew_probability"]))
        skew_ms = int(str(parameters.get("skew_ms", 0)))
        should_skew = random.random() < skew_probability
        if should_skew:
            return {"clock_skew_ms": skew_ms}
        return {}
