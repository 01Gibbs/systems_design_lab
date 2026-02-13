"""Simulator Injection Middleware - Applies scenario effects"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.application.ports.metrics import MetricsPort
from app.application.simulator.service import SimulatorService


class SimulatorInjectionMiddleware(BaseHTTPMiddleware):
    """
    Applies active scenario effects to requests/responses.

    This is where effect dicts from scenarios get executed.
    """

    def __init__(self, app: Any, metrics: MetricsPort | None = None) -> None:
        super().__init__(app)
        self.metrics = metrics

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # CRITICAL: Never apply scenarios to simulator API endpoints
        # to avoid breaking simulator control
        if request.url.path.startswith("/api/sim"):
            return await call_next(request)

        # Get active scenarios
        sim_service: SimulatorService = request.app.state.simulator_service
        status = sim_service.status()

        # Collect all effects from active scenarios
        effects = self._collect_effects(request, status.active)

        # Apply pre-request effects (e.g., delays)
        await self._apply_pre_request_effects(effects, request)

        # Call next middleware/route
        try:
            response = await call_next(request)
        except Exception:
            # Could apply error injection here
            raise

        # Apply post-response effects
        response = await self._apply_post_response_effects(effects, response)

        return response

    def _collect_effects(self, request: Request, active_scenarios: list[Any]) -> dict[str, object]:
        """Collect all effects from active scenarios"""
        sim_service: SimulatorService = request.app.state.simulator_service
        registry = sim_service._registry

        combined_effects = {}
        target = {
            "category": "http",
            "path": request.url.path,
            "method": request.method,
        }

        for active in active_scenarios:
            try:
                scenario = registry.get(active.name)
                if scenario.is_applicable(target=target):
                    ctx: Mapping[str, Any] = {"request": request, "target": target}
                    effects = scenario.apply(ctx=ctx, parameters=active.parameters)  # type: ignore
                    combined_effects.update(effects)
            except Exception:
                # Log but don't fail request
                pass

        return combined_effects

    async def _apply_pre_request_effects(
        self, effects: dict[str, object], request: Request
    ) -> None:
        """Apply effects before request processing"""
        # HTTP delay
        if "http_delay_ms" in effects:
            delay_ms = effects["http_delay_ms"]
            path_prefix = effects.get("http_path_prefix", "")
            method = effects.get("http_method", "")
            scenario_name = effects.get("scenario_name", "unknown")

            # Check if this request matches
            if (
                not path_prefix
                or (isinstance(path_prefix, str) and request.url.path.startswith(path_prefix))
            ) and (not method or request.method == method):
                if isinstance(delay_ms, (int, float)):
                    # Emit metric before applying delay
                    if self.metrics:
                        self.metrics.increment_counter(
                            "simulator_injections_total",
                            {"scenario_name": str(scenario_name), "effect_type": "http_delay"},
                        )
                    await asyncio.sleep(delay_ms / 1000.0)

    async def _apply_post_response_effects(
        self, effects: dict[str, object], response: Response
    ) -> Response:
        """Apply effects after request processing"""
        # Force error
        if effects.get("http_force_error"):
            scenario_name = effects.get("scenario_name", "unknown")

            # Emit metric
            if self.metrics:
                self.metrics.increment_counter(
                    "simulator_injections_total",
                    {"scenario_name": str(scenario_name), "effect_type": "http_error"},
                )

            # Return 500 instead
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={"detail": "Simulated error from error-burst-5xx scenario"},
            )

        return response
