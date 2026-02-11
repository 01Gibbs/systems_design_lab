"""Simulator API Contracts"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

TargetCategory = Literal["http", "db", "cpu", "algorithm"]


class ScenarioDescriptor(BaseModel):
    """Describes a scenario's metadata"""

    name: str
    description: str
    targets: list[TargetCategory]
    parameter_schema: dict[str, Any]
    safety_limits: dict[str, Any]


class ScenariosResponse(BaseModel):
    """Response for listing scenarios"""

    scenarios: list[ScenarioDescriptor]


class ActiveScenario(BaseModel):
    """An active scenario with its state"""

    name: str
    parameters: dict[str, Any]
    enabled_at: datetime
    expires_at: datetime | None = None


class StatusResponse(BaseModel):
    """Response for status endpoint"""

    active: list[ActiveScenario]


class EnableScenarioRequest(BaseModel):
    """Request to enable a scenario"""

    name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    duration_seconds: int | None = Field(default=None, ge=1, le=3600)


class DisableScenarioRequest(BaseModel):
    """Request to disable a scenario"""

    name: str
