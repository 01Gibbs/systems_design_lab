"""Prometheus metrics adapter - Infrastructure implementation"""

from typing import cast

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.application.ports.metrics import MetricsPort


class PrometheusMetrics(MetricsPort):
    """Prometheus implementation of metrics port"""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry or REGISTRY
        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}
        self._gauges: dict[str, Gauge] = {}

        # Pre-register application metrics
        self._register_application_metrics()

    def _register_application_metrics(self) -> None:
        """Register standard application metrics"""
        # HTTP metrics
        self._counters["http_requests_total"] = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self._histograms["http_request_duration_seconds"] = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        # Simulator metrics
        self._counters["simulator_scenarios_active"] = Counter(
            "simulator_scenarios_active_total",
            "Total active scenario count changes",
            ["scenario_name"],
            registry=self.registry,
        )

        self._gauges["simulator_scenarios_enabled"] = Gauge(
            "simulator_scenarios_enabled",
            "Currently enabled scenarios (1=enabled, 0=disabled)",
            ["scenario_name"],
            registry=self.registry,
        )

        self._histograms["simulator_effect_duration_seconds"] = Histogram(
            "simulator_effect_duration_seconds",
            "Time taken to apply scenario effects",
            ["scenario_name"],
            registry=self.registry,
        )

        # Business metrics
        self._counters["simulator_injections_total"] = Counter(
            "simulator_injections_total",
            "Total injections applied",
            ["scenario_name", "effect_type"],
            registry=self.registry,
        )

    def increment_counter(self, name: str, labels: dict[str, str] | None = None) -> None:
        if name in self._counters:
            if labels:
                self._counters[name].labels(**labels).inc()
            else:
                self._counters[name].inc()

    def observe_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        if name in self._histograms:
            if labels:
                self._histograms[name].labels(**labels).observe(value)
            else:
                self._histograms[name].observe(value)

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        if name in self._gauges:
            if labels:
                self._gauges[name].labels(**labels).set(value)
            else:
                self._gauges[name].set(value)

    def get_metrics(self) -> bytes:
        """Generate metrics in Prometheus format"""
        return cast(bytes, generate_latest(self.registry))
