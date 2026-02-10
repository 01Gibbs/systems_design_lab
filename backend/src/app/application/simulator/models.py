"""Application-layer models for simulator"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class ActiveScenarioState:
    """Active scenario state - application layer model"""

    name: str
    parameters: dict[str, Any]
    enabled_at: datetime
    expires_at: Optional[datetime]


@dataclass(frozen=True)
class ScenarioMeta:
    """Scenario metadata - describes what a scenario does"""

    name: str
    description: str
    targets: list[str]  # e.g., ["http", "db", "cpu"]
    parameter_schema: dict[str, Any]  # JSON schema for parameters
    safety_limits: dict[str, Any]  # max values for safety
