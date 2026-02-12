"""CPU Spike Scenario - Simulates high CPU usage on the backend"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class CpuSpike:
    """Simulates high CPU usage by introducing artificial computation delay"""

    meta = ScenarioMeta(
        name="cpu-spike",
        description="Simulates high CPU usage by burning CPU cycles.",
        targets=["http", "db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "spike_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of CPU spike on request",
                },
                "duration_ms": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 10000,
                    "description": "Duration of CPU spike in milliseconds",
                },
            },
            "required": ["spike_probability"],
        },
        safety_limits={"max_duration_ms": 10000},
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") in ("http", "db")

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        spike_probability = float(str(parameters["spike_probability"]))
        duration_ms = int(str(parameters.get("duration_ms", 1000)))
        should_spike = random.random() < spike_probability
        if should_spike:
            return {"cpu_spike_ms": duration_ms}
        return {}
