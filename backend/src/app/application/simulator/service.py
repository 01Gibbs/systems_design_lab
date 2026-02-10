"""Simulator Service - Orchestrates scenario management"""
from __future__ import annotations

from datetime import timedelta

from app.application.ports.clock import Clock
from app.application.ports.simulator_store import SimulatorStore
from app.application.simulator.models import ActiveScenarioState
from app.application.simulator.registry import ScenarioRegistry
from app.contracts.simulator import (
    ActiveScenario,
    DisableScenarioRequest,
    EnableScenarioRequest,
    ScenariosResponse,
    ScenarioDescriptor,
    StatusResponse,
)


class SimulatorService:
    """
    Application service for simulator operations.
    
    Orchestrates between registry, store, and clock (all injected).
    """

    def __init__(
        self, *, store: SimulatorStore, clock: Clock, registry: ScenarioRegistry
    ) -> None:
        self._store = store
        self._clock = clock
        self._registry = registry

    def list_scenarios(self) -> ScenariosResponse:
        """List all available scenarios"""
        out = []
        for s in self._registry.scenarios.values():
            out.append(
                ScenarioDescriptor(
                    name=s.meta.name,
                    description=s.meta.description,
                    targets=s.meta.targets,
                    parameter_schema=s.meta.parameter_schema,
                    safety_limits=s.meta.safety_limits,
                )
            )
        return ScenariosResponse(scenarios=sorted(out, key=lambda x: x.name))

    def status(self) -> StatusResponse:
        """Get status of active scenarios"""
        now = self._clock.now()
        active = []

        # Clean up expired scenarios
        for state in self._store.list_active():
            if state.expires_at is not None and state.expires_at <= now:
                self._store.remove(state.name)
                continue

            active.append(
                ActiveScenario(
                    name=state.name,
                    parameters=state.parameters,
                    enabled_at=state.enabled_at,
                    expires_at=state.expires_at,
                )
            )

        return StatusResponse(active=sorted(active, key=lambda x: x.name))

    def enable(self, req: EnableScenarioRequest) -> StatusResponse:
        """Enable a scenario with given parameters"""
        # Validate scenario exists
        scenario = self._registry.get(req.name)

        # Calculate expiry
        now = self._clock.now()
        expires_at = None
        if req.duration_seconds is not None:
            expires_at = now + timedelta(seconds=req.duration_seconds)

        # Store state
        self._store.upsert(
            ActiveScenarioState(
                name=scenario.meta.name,
                parameters=dict(req.parameters),
                enabled_at=now,
                expires_at=expires_at,
            )
        )

        return self.status()

    def disable(self, req: DisableScenarioRequest) -> StatusResponse:
        """Disable a scenario"""
        self._store.remove(req.name)
        return self.status()

    def reset(self) -> StatusResponse:
        """Disable all scenarios"""
        self._store.clear()
        return self.status()
