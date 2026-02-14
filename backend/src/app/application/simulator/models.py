"""Application-layer models for simulator"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


@dataclass(frozen=True)
class MetricSpec:
    """
    Specification for a scenario-specific metric.

    Scenarios declare metrics they emit to make their impact observable.
    This enables domain-specific observability (e.g., cache_miss_total, db_queries_per_request).
    """

    name: str
    type: Literal["counter", "gauge", "histogram", "summary"]
    description: str
    labels: list[str] = field(default_factory=list)
    buckets: list[float] | None = None  # For histograms (optional)


@dataclass(frozen=True)
class ActiveScenarioState:
    """Active scenario state - application layer model"""

    name: str
    parameters: dict[str, Any]
    enabled_at: datetime
    expires_at: datetime | None


@dataclass(frozen=True)
class ScenarioMeta:
    """Scenario metadata - describes what a scenario does"""

    name: str
    description: str
    targets: list[str]  # e.g., ["http", "db", "cpu"]
    parameter_schema: dict[str, Any]  # JSON schema for parameters
    safety_limits: dict[str, Any]  # max values for safety
    metrics: list[MetricSpec] = field(default_factory=list)  # Scenario-specific metrics
