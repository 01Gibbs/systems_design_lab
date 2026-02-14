"""Stale Read Scenario - Simulates serving stale cache data (TTL expiry, cache bypass)"""

from __future__ import annotations

import random
from dataclasses import dataclass

from prometheus_client import Counter

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class StaleRead:
    """Simulates stale cache reads (serving expired or bypassed data)"""

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        """Always applicable for cache targets (example logic)"""
        return target.get("type") == "cache"

    meta = ScenarioMeta(
        name="stale-read",
        description=(
            "Simulates serving stale cache data: requests may receive expired or bypassed values."
        ),
        targets=["cache", "http"],
        parameter_schema={
            "stale_probability": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.1},
            "cache_key_pattern": {"type": "string", "default": "*"},
        },
        safety_limits={
            "max_stale_probability": 0.9,
            "max_requests": 1000,
        },
        metrics=[
            MetricSpec(
                name="stale_read_total",
                type="counter",
                description="Total stale reads served",
                labels=["scenario", "cache_key_pattern"],
            ),
            MetricSpec(
                name="fresh_read_total",
                type="counter",
                description="Total fresh reads served",
                labels=["scenario", "cache_key_pattern"],
            ),
        ],
    )

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict simulating stale/fresh read and increments scenario metrics"""
        stale_probability = float(str(parameters["stale_probability"]))
        cache_key_pattern = str(parameters.get("cache_key_pattern", "*"))
        is_stale = random.random() < stale_probability

        metrics = ctx.get("metrics")
        if metrics:
            metrics_dict: dict[str, Counter] = metrics  # type: ignore
            if is_stale:
                metrics_dict["stale_read_total"].labels(
                    scenario="stale-read", cache_key_pattern=cache_key_pattern
                ).inc()
            else:
                metrics_dict["fresh_read_total"].labels(
                    scenario="stale-read", cache_key_pattern=cache_key_pattern
                ).inc()

        return {"is_stale": is_stale}
