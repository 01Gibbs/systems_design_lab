"""Prometheus metrics adapter - Infrastructure implementation"""

from __future__ import annotations

from typing import TYPE_CHECKING

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
)

from app.application.ports.metrics import MetricsPort

if TYPE_CHECKING:
    from app.application.simulator.models import MetricSpec


class PrometheusMetrics(MetricsPort):
    """Prometheus implementation of metrics port"""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry or REGISTRY
        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}
        self._gauges: dict[str, Gauge] = {}
        self._summaries: dict[str, Summary] = {}
        self._registered_scenario_metrics: set[str] = set()  # Track registered scenarios

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

    def register_scenario_metrics(self, scenario_name: str, metrics: list[MetricSpec]) -> None:
        """
        Register scenario-specific metrics dynamically.

        Args:
            scenario_name: Name of the scenario (for tracking)
            metrics: List of metric specifications to register
        """
        # Only register once per scenario
        if scenario_name in self._registered_scenario_metrics:
            return

        for metric_spec in metrics:
            metric_name = metric_spec.name

            # Skip if already registered (avoid collisions)
            if metric_name in {
                **self._counters,
                **self._histograms,
                **self._gauges,
                **self._summaries,
            }:
                continue

            try:
                if metric_spec.type == "counter":
                    self._counters[metric_name] = Counter(
                        metric_name,
                        metric_spec.description,
                        metric_spec.labels,
                        registry=self.registry,
                    )
                elif metric_spec.type == "gauge":
                    self._gauges[metric_name] = Gauge(
                        metric_name,
                        metric_spec.description,
                        metric_spec.labels,
                        registry=self.registry,
                    )
                elif metric_spec.type == "histogram":
                    # Use custom buckets if specified, otherwise use default
                    if metric_spec.buckets:
                        self._histograms[metric_name] = Histogram(
                            metric_name,
                            metric_spec.description,
                            metric_spec.labels,
                            buckets=metric_spec.buckets,
                            registry=self.registry,
                        )
                    else:
                        self._histograms[metric_name] = Histogram(
                            metric_name,
                            metric_spec.description,
                            metric_spec.labels,
                            registry=self.registry,
                        )
                elif metric_spec.type == "summary":
                    self._summaries[metric_name] = Summary(
                        metric_name,
                        metric_spec.description,
                        metric_spec.labels,
                        registry=self.registry,
                    )
            except Exception:
                # If registration fails (e.g., duplicate), continue with others
                # This is a safety fallback - should not happen in normal operation
                continue

        self._registered_scenario_metrics.add(scenario_name)

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
        return generate_latest(self.registry)
