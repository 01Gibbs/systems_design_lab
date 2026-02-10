"""FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.simulator.registry import get_registry


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events - startup and shutdown"""
    # Startup: Register scenarios
    registry = get_registry()

    # TODO: Register initial scenarios here
    # Example:
    # from backend.simulator.scenarios.latency_fixed import LatencyFixedScenario
    # registry.register(LatencyFixedScenario())

    print("✓ Application started")

    yield

    # Shutdown: Cleanup
    print("✓ Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="Systems Design Lab API",
    description="Production-grade systems design lab for simulating real-world issues",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "Systems Design Lab API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


# TODO: Add simulator API routes
# from backend.api.simulator import router as simulator_router
# app.include_router(simulator_router, prefix="/api/sim", tags=["simulator"])
