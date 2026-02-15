"""Retry Storm Scenario - Simulates cascading retries overwhelming a service"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class RetryStorm:
    """Simulates retry storm where failed requests trigger exponential retry attempts"""

    meta = ScenarioMeta(
        name="retry-storm",
        description="Simulates retry storm: multiplies request load through cascading retries.",
        targets=["http"],
        parameter_schema={
            "type": "object",
            "properties": {
                "failure_rate": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of request failure triggering retries",
                },
                "retry_multiplier": {
                    "type": "number",
                    "minimum": 1.0,
                    "maximum": 10.0,
                    "description": "Request count multiplier per retry",
                },
                "status_code": {
                    "type": "integer",
                    "minimum": 500,
                    "maximum": 599,
                    "description": "HTTP status code for failed requests",
                },
                "path_prefix": {"type": "string"},
            },
            "required": ["failure_rate"],
        },
        safety_limits={"max_retry_multiplier": 10.0},
        metrics=[
            MetricSpec(
                name="retry_attempts_total",
                type="counter",
                description="Total number of retry attempts by scenario",
                labels=["scenario"],
            ),
            MetricSpec(
                name="retry_depth",
                type="histogram",
                description="Retry depth/count per request",
                labels=["scenario"],
                buckets=[1, 2, 3, 5, 10, 20],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "http"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict simulating retry storm behavior"""
        failure_rate = float(str(parameters["failure_rate"]))
        retry_multiplier = float(str(parameters.get("retry_multiplier", 2.0)))
        status_code = int(str(parameters.get("status_code", 503)))
        path_prefix = str(parameters.get("path_prefix", ""))

        # Simulate whether this request should fail and trigger retries
        should_fail = random.random() < failure_rate

        if should_fail:
            return {
                "retry_storm_active": True,
                "http_status": status_code,
                "http_path_prefix": path_prefix,
                "retry_multiplier": retry_multiplier,
            }

        return {}
