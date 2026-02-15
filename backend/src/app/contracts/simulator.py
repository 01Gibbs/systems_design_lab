"""Simulator API Contracts"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# Type aliases defined inline to keep contracts layer standalone (no imports from other layers)
JsonSchema = dict[str, object]
ParameterValue = (
    str
    | int
    | float
    | bool
    | None
    | dict[str, str | int | float | bool | None]
    | list[str | int | float | bool | None]
)
Parameters = dict[str, ParameterValue]

TargetCategory = Literal["http", "db", "cpu", "algorithm"]


class ScenarioDescriptor(BaseModel):
    """Describes a scenario's metadata"""

    name: str
    description: str
    targets: list[TargetCategory]
    parameter_schema: JsonSchema
    safety_limits: JsonSchema


class ScenariosResponse(BaseModel):
    """Response for listing scenarios"""

    scenarios: list[ScenarioDescriptor]


class ActiveScenario(BaseModel):
    """An active scenario with its state"""

    name: str
    parameters: Parameters
    enabled_at: datetime
    expires_at: datetime | None = None


class StatusResponse(BaseModel):
    """Response for status endpoint"""

    active: list[ActiveScenario]


class EnableScenarioRequest(BaseModel):
    """Request to enable a scenario"""

    name: str
    parameters: Parameters = Field(default_factory=dict)
    duration_seconds: int | None = Field(default=None, ge=1, le=3600)


class DisableScenarioRequest(BaseModel):
    """Request to disable a scenario"""

    name: str
