"""Metrics port - abstraction for domain/application layers"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.simulator.models import MetricSpec


class MetricsPort(ABC):
    """Abstract metrics interface - no framework dependencies"""

    @abstractmethod
    def increment_counter(self, name: str, labels: dict[str, str] | None = None) -> None:
        """Increment a counter metric"""
        pass

    @abstractmethod
    def observe_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Record histogram observation"""
        pass

    @abstractmethod
    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set gauge value"""
        pass

    @abstractmethod
    def register_scenario_metrics(self, scenario_name: str, metrics: list[MetricSpec]) -> None:
        """
        Register scenario-specific metrics dynamically.

        Args:
            scenario_name: Name of the scenario (for prefixing/context)
            metrics: List of metric specifications to register
        """
        pass

    @abstractmethod
    def get_metrics(self) -> bytes:
        """Get metrics in exportable format"""
        pass
