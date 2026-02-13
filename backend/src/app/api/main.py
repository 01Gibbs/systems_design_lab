"""FastAPI Application - Composition Root with DI"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.simulator_injection import SimulatorInjectionMiddleware
from app.api.routers.health import router as health_router
from app.api.routers.metrics import router as metrics_router
from app.api.routers.simulator import router as simulator_router
from app.application.simulator.registry import build_registry
from app.application.simulator.service import SimulatorService
from app.infrastructure.observability.logging import setup_logging
from app.infrastructure.observability.metrics import PrometheusMetrics
from app.infrastructure.observability.middleware import ObservabilityMiddleware
from app.infrastructure.observability.tracing import instrument_fastapi, setup_tracing
from app.infrastructure.simulator.memory_store import InMemorySimulatorStore
from app.infrastructure.time.system_clock import SystemClock

# Setup logging first (before any other imports that log)
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    json_format=os.getenv("LOG_JSON", "false").lower() == "true",
)

# Setup tracing
setup_tracing(app_name=os.getenv("OTEL_SERVICE_NAME", "systems-design-lab-backend"))


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

    # Instrument FastAPI with OpenTelemetry tracing
    instrument_fastapi(app)

    # Infrastructure implementations (adapters)
    store = InMemorySimulatorStore()
    clock = SystemClock()
    registry = build_registry()
    metrics = PrometheusMetrics()

    # Store metrics in app state for routers and middleware to access
    app.state.metrics = metrics

    # Application services (use cases) - inject metrics port
    sim_service = SimulatorService(store=store, clock=clock, registry=registry, metrics=metrics)

    # Store in app state for routers to access
    app.state.simulator_service = sim_service

    # Middleware (order matters - last added runs first)
    # CORS is outermost
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite default
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Observability tracks all requests (after CORS)
    app.add_middleware(ObservabilityMiddleware, metrics=metrics)
    # Simulator injection applies effects (after observability)
    app.add_middleware(SimulatorInjectionMiddleware, metrics=metrics)
    # Request ID is innermost (runs first)
    app.add_middleware(RequestIdMiddleware)

    # Routers
    app.include_router(health_router, prefix="/api")
    app.include_router(metrics_router, prefix="/api")
    app.include_router(simulator_router, prefix="/api/sim")

    return app


# Create app instance
app = create_app()
