"""In-Memory Simulator Store Implementation"""

from __future__ import annotations

from app.application.ports.simulator_store import SimulatorStore
from app.application.simulator.models import ActiveScenarioState


class InMemorySimulatorStore(SimulatorStore):
    """
    In-memory implementation of SimulatorStore.

    Perfect for local development and testing.
    Could be swapped for Redis or database-backed store.
    """

    def __init__(self) -> None:
        self._store: dict[str, ActiveScenarioState] = {}

    def list_active(self) -> list[ActiveScenarioState]:
        return list(self._store.values())

    def upsert(self, state: ActiveScenarioState) -> None:
        self._store[state.name] = state

    def remove(self, name: str) -> None:
        self._store.pop(name, None)

    def clear(self) -> None:
        self._store.clear()

    def get(self, name: str) -> ActiveScenarioState | None:
        return self._store.get(name)
