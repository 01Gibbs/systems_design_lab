"""Simulator Injection Middleware - Applies scenario effects"""
from __future__ import annotations

import asyncio

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.application.simulator.service import SimulatorService


class SimulatorInjectionMiddleware(BaseHTTPMiddleware):
    """
    Applies active scenario effects to requests/responses.
    
    This is where effect dicts from scenarios get executed.
    """

    async def dispatch(self, request: Request, call_next):
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
        except Exception as e:
            # Could apply error injection here
            raise

        # Apply post-response effects
        response = await self._apply_post_response_effects(effects, response)

        return response

    def _collect_effects(self, request: Request, active_scenarios) -> dict:
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
                    ctx = {"request": request, "target": target}
                    effects = scenario.apply(ctx=ctx, parameters=active.parameters)
                    combined_effects.update(effects)
            except Exception:
                # Log but don't fail request
                pass

        return combined_effects

    async def _apply_pre_request_effects(
        self, effects: dict, request: Request
    ) -> None:
        """Apply effects before request processing"""
        # HTTP delay
        if "http_delay_ms" in effects:
            delay_ms = effects["http_delay_ms"]
            path_prefix = effects.get("http_path_prefix", "")
            method = effects.get("http_method", "")

            # Check if this request matches
            if (not path_prefix or request.url.path.startswith(path_prefix)) and (
                not method or request.method == method
            ):
                await asyncio.sleep(delay_ms / 1000.0)

    async def _apply_post_response_effects(
        self, effects: dict, response: Response
    ) -> Response:
        """Apply effects after request processing"""
        # Force error
        if effects.get("http_force_error"):
            # Return 500 instead
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={"detail": "Simulated error from error-burst-5xx scenario"},
            )

        return response
