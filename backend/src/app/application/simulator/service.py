"""Simulator Service - Orchestrates scenario management"""

from __future__ import annotations

from datetime import timedelta

from app.application.ports.clock import Clock
from app.application.ports.simulator_store import SimulatorStore
from app.application.simulator.app_models import (
    ActiveScenarioApp,
    DisableScenarioRequestApp,
    EnableScenarioRequestApp,
    ScenarioDescriptorApp,
    ScenariosResponseApp,
    StatusResponseApp,
)
from app.application.simulator.exceptions import ScenarioNotFoundError
from app.application.simulator.models import ActiveScenarioState
from app.application.simulator.registry import ScenarioRegistry


class SimulatorService:
    """
    Application service for simulator operations.

    Orchestrates between registry, store, and clock (all injected).
    """

    def __init__(self, *, store: SimulatorStore, clock: Clock, registry: ScenarioRegistry) -> None:
        self._store = store
        self._clock = clock
        self._registry = registry

    def list_scenarios(self) -> ScenariosResponseApp:
        """List all available scenarios"""
        out = []
        for s in self._registry.scenarios.values():
            out.append(
                ScenarioDescriptorApp(
                    name=s.meta.name,
                    description=s.meta.description,
                    targets=[t for t in s.meta.targets],
                    parameter_schema=s.meta.parameter_schema,
                    safety_limits=s.meta.safety_limits,
                )
            )
        return ScenariosResponseApp(scenarios=sorted(out, key=lambda x: x.name))

    def status(self) -> StatusResponseApp:
        """Get status of active scenarios"""
        now = self._clock.now()
        active = []

        # Clean up expired scenarios
        for state in self._store.list_active():
            if state.expires_at is not None and state.expires_at <= now:
                self._store.remove(state.name)
                continue

            active.append(
                ActiveScenarioApp(
                    name=state.name,
                    parameters=state.parameters,
                    enabled_at=state.enabled_at,
                    expires_at=state.expires_at,
                )
            )

        return StatusResponseApp(active=sorted(active, key=lambda x: x.name))

    def enable(self, req: EnableScenarioRequestApp) -> StatusResponseApp:
        """Enable a scenario with given parameters"""
        # Validate scenario exists
        try:
            scenario = self._registry.get(req.name)
        except KeyError as e:
            raise ScenarioNotFoundError(req.name) from e

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

    def disable(self, req: DisableScenarioRequestApp) -> StatusResponseApp:
        """Disable a scenario"""
        self._store.remove(req.name)
        return self.status()

    def reset(self) -> StatusResponseApp:
        """Disable all scenarios"""
        self._store.clear()
        return self.status()
