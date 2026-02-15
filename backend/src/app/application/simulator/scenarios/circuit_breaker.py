"""Circuit Breaker Scenario - Simulates service degradation with circuit breaker behavior"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class CircuitBreaker:
    """Simulates circuit breaker opening after consecutive failures"""

    meta = ScenarioMeta(
        name="circuit-breaker",
        description=(
            "Simulates circuit breaker pattern: fails requests after "
            "threshold failures, then enters half-open state."
        ),
        targets=["http"],
        parameter_schema={
            "type": "object",
            "properties": {
                "failure_threshold": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Number of failures before circuit opens",
                },
                "timeout_ms": {
                    "type": "integer",
                    "minimum": 100,
                    "maximum": 60000,
                    "description": "Circuit breaker timeout before half-open",
                },
                "path_prefix": {"type": "string"},
                "status_code": {
                    "type": "integer",
                    "minimum": 500,
                    "maximum": 599,
                    "description": "HTTP status code to return when circuit is open",
                },
            },
            "required": ["failure_threshold"],
        },
        safety_limits={"max_timeout_ms": 60000},
        metrics=[
            MetricSpec(
                name="circuit_breaker_state",
                type="gauge",
                description="Circuit breaker state (0=closed, 1=open, 2=half-open)",
                labels=["scenario"],
            ),
            MetricSpec(
                name="circuit_breaker_trips_total",
                type="counter",
                description="Total number of circuit breaker trips by scenario",
                labels=["scenario"],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "http"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict simulating circuit breaker behavior"""
        # Note: failure_threshold would be used in production to track actual failures
        # For simulation purposes, we use random probability
        timeout_ms = int(str(parameters.get("timeout_ms", 5000)))
        status_code = int(str(parameters.get("status_code", 503)))
        path_prefix = str(parameters.get("path_prefix", ""))
        # Simple simulation: randomly decide if circuit should be open
        is_circuit_open = random.random() < 0.3  # 30% chance circuit is open

        if is_circuit_open:
            return {
                "circuit_breaker_open": True,
                "http_status": status_code,
                "http_path_prefix": path_prefix,
                "http_delay_ms": timeout_ms,
            }

        return {}
