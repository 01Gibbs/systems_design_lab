"""Scenario Registry - Central registration and lookup"""

from __future__ import annotations

from typing import Protocol

from app.application.simulator.models import ScenarioMeta


class Scenario(Protocol):
    """
    Protocol for simulator scenarios.

    Scenarios return EFFECTS (dicts) rather than executing side effects.
    This keeps simulator logic isolated and testable.
    """

    meta: ScenarioMeta

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        """Check if scenario applies to this target"""
        ...

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """
        Returns a dict of effects for middleware/adapters to apply.
        NO direct side effects here.

        Example return values:
        - {"http_delay_ms": 100} - delay HTTP response
        - {"http_force_error": True} - force 500 error
        - {"db_sleep_seconds": 2.0} - add DB delay
        """
        ...


class ScenarioRegistry:
    """Registry of all available scenarios"""

    def __init__(self, scenarios: dict[str, Scenario]):
        self._scenarios = scenarios

    @property
    def scenarios(self) -> dict[str, Scenario]:
        return self._scenarios

    def get(self, name: str) -> Scenario:
        """Get a scenario by name"""
        if name not in self._scenarios:
            raise KeyError(f"Unknown scenario '{name}'")
        return self._scenarios[name]


def build_registry() -> ScenarioRegistry:
    """Build the registry with all available scenarios"""
    from app.application.simulator.scenarios.algorithmic_degradation import (
        AlgorithmicDegradation,
    )
    from app.application.simulator.scenarios.error_burst import ErrorBurst
    from app.application.simulator.scenarios.fixed_latency import FixedLatency
    from app.application.simulator.scenarios.lock_contention import LockContention
    from app.application.simulator.scenarios.slow_db_query import SlowDbQuery

    items: list[Scenario] = [
        FixedLatency(),
        ErrorBurst(),
        SlowDbQuery(),
        LockContention(),
        AlgorithmicDegradation(),
    ]
    return ScenarioRegistry({s.meta.name: s for s in items})
