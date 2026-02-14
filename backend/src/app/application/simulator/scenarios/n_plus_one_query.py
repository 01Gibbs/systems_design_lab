"""N+1 Query Scenario - Simulates N+1 query problem with observable query counts"""

from __future__ import annotations

import random
from dataclasses import dataclass

from prometheus_client import Counter, Histogram

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class NPlusOneQuery:
    """Simulates N+1 query problem where N queries are made instead of 1 optimized query"""

    meta = ScenarioMeta(
        name="n-plus-one-query",
        description=(
            "Simulates N+1 query problem: "
            "1 query for list + N queries for related data instead of optimized join."
        ),
        targets=["db"],
        parameter_schema={
            "n_items": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Number of items fetched (determines N in N+1)",
                "default": 10,
            },
            "extra_query_delay_ms": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Delay per extra query in milliseconds",
                "default": 10,
            },
            "probability": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Probability of N+1 pattern occurring",
                "default": 0.5,
            },
        },
        safety_limits={
            "max_n_items": 100,
            "max_extra_query_delay_ms": 100,
            "max_total_delay_ms": 10000,
        },
        metrics=[
            MetricSpec(
                name="db_queries_per_request",
                type="histogram",
                description="Number of DB queries per HTTP request",
                labels=["scenario", "pattern"],
                buckets=[1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0],
            ),
            MetricSpec(
                name="db_query_count_total",
                type="counter",
                description="Total database queries executed",
                labels=["scenario", "query_type"],
            ),
            MetricSpec(
                name="n_plus_one_detected_total",
                type="counter",
                description="Number of times N+1 pattern was detected",
                labels=["scenario"],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        """Applies to database operations"""
        return target.get("category") == "db"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict simulating N+1 query pattern and increments scenario metrics"""
        n_items = int(str(parameters.get("n_items", 10)))
        extra_query_delay_ms = int(str(parameters.get("extra_query_delay_ms", 10)))
        probability = float(str(parameters.get("probability", 0.5)))

        # Determine if N+1 pattern triggers
        is_n_plus_one = random.random() < probability

        if is_n_plus_one:
            # N+1 pattern: 1 initial query + N additional queries
            query_count = 1 + n_items
            total_delay_ms = extra_query_delay_ms * n_items
            pattern = "n_plus_one"
        else:
            # Optimized: 1 query with JOIN or similar
            query_count = 1
            total_delay_ms = 0
            pattern = "optimized"

        # Update metrics
        metrics = ctx.get("metrics")
        if metrics:
            metrics_dict: dict[str, Counter | Histogram] = metrics  # type: ignore

            # Record queries per request (histogram)
            histogram = metrics_dict["db_queries_per_request"]
            assert hasattr(histogram, "observe")
            histogram.labels(scenario="n-plus-one-query", pattern=pattern).observe(query_count)

            # Record total query count (counter)
            counter = metrics_dict["db_query_count_total"]
            assert hasattr(counter, "inc")
            counter.labels(scenario="n-plus-one-query", query_type=pattern).inc(query_count)

            # Record N+1 detection (counter)
            if is_n_plus_one:
                detection_counter = metrics_dict["n_plus_one_detected_total"]
                assert hasattr(detection_counter, "inc")
                detection_counter.labels(scenario="n-plus-one-query").inc()

        return {
            "db_query_count": query_count,
            "db_delay_ms": total_delay_ms,
            "is_n_plus_one": is_n_plus_one,
            "pattern": pattern,
        }
