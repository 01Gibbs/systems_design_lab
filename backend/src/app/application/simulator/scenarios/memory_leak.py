"""Memory Leak Scenario - Simulates gradual memory consumption over time"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class MemoryLeak:
    """Simulates memory leak by increasing memory usage on each request"""

    meta = ScenarioMeta(
        name="memory-leak",
        description="Simulates memory leak: increases memory usage over time.",
        targets=["http", "database"],
        parameter_schema={
            "type": "object",
            "properties": {
                "leak_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of memory leak on request",
                },
                "leak_size_kb": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10240,
                    "description": "Amount of memory to leak in KB",
                },
            },
            "required": ["leak_probability"],
        },
        safety_limits={"max_leak_size_kb": 10240},
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") in ("http", "database")

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        leak_probability = float(str(parameters["leak_probability"]))
        leak_size_kb = int(str(parameters.get("leak_size_kb", 1024)))
        should_leak = random.random() < leak_probability
        if should_leak:
            return {"memory_leak_kb": leak_size_kb}
        return {}
