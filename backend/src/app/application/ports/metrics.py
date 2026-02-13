"""Metrics port - abstraction for domain/application layers"""

from abc import ABC, abstractmethod


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
    def get_metrics(self) -> bytes:
        """Get metrics in exportable format"""
        pass
