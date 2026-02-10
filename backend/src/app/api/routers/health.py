"""Health Check Router"""
from __future__ import annotations

from fastapi import APIRouter

from app.contracts.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="0.1.0")
