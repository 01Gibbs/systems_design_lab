"""Cache Stampede Scenario - Simulates thundering herd when cache expires"""

from __future__ import annotations

import random
from dataclasses import dataclass

from prometheus_client import Counter

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class CacheStampede:
    """Simulates cache stampede (thundering herd) when popular cache key expires"""

    meta = ScenarioMeta(
        name="cache-stampede",
        description=(
            "Simulates cache stampede: multiple requests simultaneously "
            "query backend when cache expires."
        ),
        targets=["db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "stampede_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of cache miss triggering stampede",
                },
                "concurrent_requests": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 1000,
                    "description": "Number of concurrent requests hitting backend",
                },
                "backend_delay_ms": {
                    "type": "integer",
                    "minimum": 100,
                    "maximum": 30000,
                    "description": "Backend query duration during stampede",
                },
                "cache_key_pattern": {"type": "string"},
            },
            "required": ["stampede_probability"],
        },
        safety_limits={"max_concurrent_requests": 1000, "max_backend_delay_ms": 30000},
        metrics=[
            MetricSpec(
                name="cache_hit_total",
                type="counter",
                description="Total number of cache hits during scenario",
                labels=["scenario", "cache_key_pattern"],
            ),
            MetricSpec(
                name="cache_miss_total",
                type="counter",
                description="Total number of cache misses during scenario",
                labels=["scenario", "cache_key_pattern"],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        category = target.get("category", "")
        return category == "db"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict simulating cache stampede and increments scenario metrics"""
        stampede_probability = float(str(parameters["stampede_probability"]))
        concurrent_requests = int(str(parameters.get("concurrent_requests", 100)))
        backend_delay_ms = int(str(parameters.get("backend_delay_ms", 5000)))
        cache_key_pattern = str(parameters.get("cache_key_pattern", "*"))
        # Simulate whether stampede is occurring
        is_stampede = random.random() < stampede_probability

        # Metric increment logic (scenario-specific)

        metrics = ctx.get("metrics")
        if metrics:
            metrics_dict: dict[str, Counter] = metrics  # type: ignore
            if is_stampede:
                # Cache miss triggers stampede
                metrics_dict["cache_miss_total"].labels(
                    scenario="cache-stampede", cache_key_pattern=cache_key_pattern
                ).inc()
            else:
                # Cache hit avoids backend query
                metrics_dict["cache_hit_total"].labels(
                    scenario="cache-stampede", cache_key_pattern=cache_key_pattern
                ).inc()

        if is_stampede:
            return {
                "cache_stampede_active": True,
                "cache_miss": True,
                "concurrent_backend_requests": concurrent_requests,
                "db_query_delay_ms": backend_delay_ms,
                "cache_key_pattern": cache_key_pattern,
            }

        return {}
