"""Application-layer models for simulator (no contracts dependency)"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ScenarioDescriptorApp:
    name: str
    description: str
    targets: list[str]
    parameter_schema: dict[str, Any]
    safety_limits: dict[str, Any]


@dataclass(frozen=True)
class ScenariosResponseApp:
    scenarios: list[ScenarioDescriptorApp]


@dataclass(frozen=True)
class ActiveScenarioApp:
    name: str
    parameters: dict[str, Any]
    enabled_at: datetime
    expires_at: datetime | None = None


@dataclass(frozen=True)
class StatusResponseApp:
    active: list[ActiveScenarioApp]


@dataclass(frozen=True)
class EnableScenarioRequestApp:
    name: str
    parameters: dict[str, Any]
    duration_seconds: int | None = None


@dataclass(frozen=True)
class DisableScenarioRequestApp:
    name: str
