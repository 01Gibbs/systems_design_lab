"""Resource Starvation Scenario - Simulates thread or worker pool exhaustion"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class ResourceStarvation:
    """Simulates resource starvation by limiting available worker threads/processes"""

    meta = ScenarioMeta(
        name="resource-starvation",
        description="Simulates resource starvation: limits available worker threads/processes.",
        targets=["http", "db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "starvation_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of resource starvation event",
                },
                "max_workers": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Simulated max worker pool size",
                },
            },
            "required": ["starvation_probability"],
        },
        safety_limits={"max_workers": 100},
        metrics=[
            MetricSpec(
                name="resource_queue_depth",
                type="gauge",
                description="Resource queue depth by scenario",
                labels=["scenario"],
            ),
            MetricSpec(
                name="resource_wait_seconds",
                type="histogram",
                description="Resource wait time (seconds)",
                labels=["scenario"],
                buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") in ("http", "database")

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        starvation_probability = float(str(parameters["starvation_probability"]))
        max_workers = int(str(parameters.get("max_workers", 10)))
        should_starve = random.random() < starvation_probability
        if should_starve:
            return {"resource_starvation": True, "max_workers": max_workers}
        return {}
