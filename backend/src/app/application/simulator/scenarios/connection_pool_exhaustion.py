"""Connection Pool Exhaustion Scenario - Simulates database connection pool depletion"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class ConnectionPoolExhaustion:
    """Simulates database connection pool exhaustion"""

    meta = ScenarioMeta(
        name="connection-pool-exhaustion",
        description="Simulates connection pool exhaustion by making DB connections hang or fail.",
        targets=["db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "exhaustion_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of connection acquisition failing",
                },
                "hang_duration_ms": {
                    "type": "integer",
                    "minimum": 100,
                    "maximum": 30000,
                    "description": "Duration connections hang before timing out",
                },
                "pool_size_limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Simulated max pool size",
                },
            },
            "required": ["exhaustion_probability"],
        },
        safety_limits={"max_hang_duration_ms": 30000},
        metrics=[
            MetricSpec(
                name="connection_pool_size",
                type="gauge",
                description="Current connection pool size by scenario",
                labels=["scenario"],
            ),
            MetricSpec(
                name="connection_pool_wait_seconds",
                type="histogram",
                description="Connection pool wait time (seconds)",
                labels=["scenario"],
                buckets=[0.1, 0.5, 1, 2, 5, 10, 30],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "db"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict simulating connection pool exhaustion"""
        exhaustion_probability = float(str(parameters["exhaustion_probability"]))
        hang_duration_ms = int(str(parameters.get("hang_duration_ms", 5000)))
        pool_size_limit = int(str(parameters.get("pool_size_limit", 10)))

        # Simulate whether connection pool is exhausted
        is_exhausted = random.random() < exhaustion_probability

        if is_exhausted:
            return {
                "db_connection_exhausted": True,
                "db_hang_duration_ms": hang_duration_ms,
                "db_pool_size_limit": pool_size_limit,
            }

        return {}
