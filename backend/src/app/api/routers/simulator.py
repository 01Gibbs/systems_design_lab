"""Simulator API Router"""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.application.simulator.service import SimulatorService
from app.contracts.simulator import (
    DisableScenarioRequest,
    EnableScenarioRequest,
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
    return _get_service(request).list_scenarios()


@router.get("/status", response_model=StatusResponse)
async def status(request: Request) -> StatusResponse:
    """Get status of active scenarios"""
    return _get_service(request).status()


@router.post("/enable", response_model=StatusResponse)
async def enable(request: Request, body: EnableScenarioRequest) -> StatusResponse:
    """Enable a scenario"""
    return _get_service(request).enable(body)


@router.post("/disable", response_model=StatusResponse)
async def disable(request: Request, body: DisableScenarioRequest) -> StatusResponse:
    """Disable a scenario"""
    return _get_service(request).disable(body)


@router.post("/reset", response_model=StatusResponse)
async def reset(request: Request) -> StatusResponse:
    """Disable all scenarios"""
    return _get_service(request).reset()
