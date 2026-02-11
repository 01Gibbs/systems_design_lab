"""SimulatorStore Port - Interface for active scenario persistence"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.application.simulator.models import ActiveScenarioState


class SimulatorStore(ABC):
    """Port for storing active scenario state"""

    @abstractmethod
    def list_active(self) -> list[ActiveScenarioState]:
        """List all active scenarios"""
        raise NotImplementedError

    @abstractmethod
    def upsert(self, state: ActiveScenarioState) -> None:
        """Insert or update a scenario state"""
        raise NotImplementedError

    @abstractmethod
    def remove(self, name: str) -> None:
        """Remove a scenario by name"""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all active scenarios"""
        raise NotImplementedError

    @abstractmethod
    def get(self, name: str) -> ActiveScenarioState | None:
        """Get a specific scenario by name"""
        raise NotImplementedError
