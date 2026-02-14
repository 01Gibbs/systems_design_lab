"""Simulator API Router"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.application.simulator.app_models import (
    DisableScenarioRequestApp,
    EnableScenarioRequestApp,
    ScenariosResponseApp,
    StatusResponseApp,
)
from app.application.simulator.exceptions import ScenarioNotFoundError
from app.application.simulator.service import SimulatorService
from app.contracts.simulator import (
    ActiveScenario,
    DisableScenarioRequest,
    EnableScenarioRequest,
    ScenarioDescriptor,
    ScenariosResponse,
    StatusResponse,
)

router = APIRouter(tags=["simulator"])


def _get_service(request: Request) -> SimulatorService:
    """Get simulator service from app state"""
    return request.app.state.simulator_service  # type: ignore


@router.get("/scenarios", response_model=ScenariosResponse)
async def list_scenarios(request: Request) -> ScenariosResponse:
    """List all available scenarios"""
    app_resp: ScenariosResponseApp = _get_service(request).list_scenarios()
    # Map app-layer models to contract models
    return ScenariosResponse(
        scenarios=[
            ScenarioDescriptor(
                name=s.name,
                description=s.description,
                targets=list(s.targets),
                parameter_schema=s.parameter_schema,
                safety_limits=s.safety_limits,
            )
            for s in app_resp.scenarios
        ]
    )


@router.get("/status", response_model=StatusResponse)
async def status(request: Request) -> StatusResponse:
    """Get status of active scenarios"""
    app_resp: StatusResponseApp = _get_service(request).status()
    return StatusResponse(
        active=[
            ActiveScenario(
                name=a.name,
                parameters=a.parameters,
                enabled_at=a.enabled_at,
                expires_at=a.expires_at,
            )
            for a in app_resp.active
        ]
    )


@router.post("/enable", response_model=StatusResponse)
async def enable(request: Request, body: EnableScenarioRequest) -> StatusResponse:
    """Enable a scenario"""
    try:
        app_req = EnableScenarioRequestApp(
            name=body.name,
            parameters=body.parameters,
            duration_seconds=body.duration_seconds,
        )
        app_resp: StatusResponseApp = _get_service(request).enable(app_req)
        return StatusResponse(
            active=[
                ActiveScenario(
                    name=a.name,
                    parameters=a.parameters,
                    enabled_at=a.enabled_at,
                    expires_at=a.expires_at,
                )
                for a in app_resp.active
            ]
        )
    except ScenarioNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/disable", response_model=StatusResponse)
async def disable(request: Request, body: DisableScenarioRequest) -> StatusResponse:
    """Disable a scenario"""
    app_req = DisableScenarioRequestApp(name=body.name)
    app_resp: StatusResponseApp = _get_service(request).disable(app_req)
    return StatusResponse(
        active=[
            ActiveScenario(
                name=a.name,
                parameters=a.parameters,
                enabled_at=a.enabled_at,
                expires_at=a.expires_at,
            )
            for a in app_resp.active
        ]
    )


@router.post("/reset", response_model=StatusResponse)
async def reset(request: Request) -> StatusResponse:
    """Disable all scenarios"""
    app_resp: StatusResponseApp = _get_service(request).reset()
    return StatusResponse(
        active=[
            ActiveScenario(
                name=a.name,
                parameters=a.parameters,
                enabled_at=a.enabled_at,
                expires_at=a.expires_at,
            )
            for a in app_resp.active
        ]
    )
