"""FastAPI Application - Composition Root with DI"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.simulator_injection import SimulatorInjectionMiddleware
from app.api.routers.health import router as health_router
from app.api.routers.simulator import router as simulator_router
from app.application.simulator.registry import build_registry
from app.application.simulator.service import SimulatorService
from app.infrastructure.simulator.memory_store import InMemorySimulatorStore
from app.infrastructure.time.system_clock import SystemClock


def create_app() -> FastAPI:
    """
    Composition root - wire dependencies here.

    This is where we do dependency injection explicitly.
    Infrastructure implementations are created and injected into
    application services.
    """
    app = FastAPI(
        title="Local Systems Design Lab",
        version="0.1.0",
        description="Production-grade systems design lab for simulating real-world issues",
    )

    # Infrastructure implementations (adapters)
    store = InMemorySimulatorStore()
    clock = SystemClock()
    registry = build_registry()

    # Application services (use cases)
    sim_service = SimulatorService(store=store, clock=clock, registry=registry)

    # Store in app state for routers to access
    app.state.simulator_service = sim_service

    # Middleware (order matters - last added runs first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite default
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SimulatorInjectionMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # Routers
    app.include_router(health_router, prefix="/api")
    app.include_router(simulator_router, prefix="/api/sim")

    return app


# Create app instance
app = create_app()
