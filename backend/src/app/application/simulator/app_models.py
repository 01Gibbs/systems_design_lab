"""Application-layer models for simulator (no contracts dependency)"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.types import JsonSchema, Parameters


@dataclass(frozen=True)
class ScenarioDescriptorApp:
    name: str
    description: str
    targets: list[str]
    parameter_schema: JsonSchema
    safety_limits: JsonSchema


@dataclass(frozen=True)
class ScenariosResponseApp:
    scenarios: list[ScenarioDescriptorApp]


@dataclass(frozen=True)
class ActiveScenarioApp:
    name: str
    parameters: Parameters
    enabled_at: datetime
    expires_at: datetime | None = None


@dataclass(frozen=True)
class StatusResponseApp:
    active: list[ActiveScenarioApp]


@dataclass(frozen=True)
class EnableScenarioRequestApp:
    name: str
    parameters: Parameters
    duration_seconds: int | None = None


@dataclass(frozen=True)
class DisableScenarioRequestApp:
    name: str
