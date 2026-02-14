"""Tests for scenario-specific metrics functionality"""

import pytest
from prometheus_client import CollectorRegistry

from app.application.simulator.models import MetricSpec
from app.infrastructure.observability.metrics import PrometheusMetrics


class TestMetricSpec:
    """Tests for MetricSpec dataclass"""

    def test_metric_spec_counter(self):
        """Test creating a counter metric spec"""
        spec = MetricSpec(
            name="test_counter_total",
            type="counter",
            description="Test counter metric",
            labels=["scenario", "endpoint"],
        )

        assert spec.name == "test_counter_total"
        assert spec.type == "counter"
        assert spec.description == "Test counter metric"
        assert spec.labels == ["scenario", "endpoint"]
        assert spec.buckets is None

    def test_metric_spec_histogram_with_buckets(self):
        """Test creating a histogram metric spec with custom buckets"""
        buckets = [0.1, 0.5, 1.0, 5.0, 10.0]
        spec = MetricSpec(
            name="test_duration_seconds",
            type="histogram",
            description="Test histogram metric",
            labels=["endpoint"],
            buckets=buckets,
        )

        assert spec.name == "test_duration_seconds"
        assert spec.type == "histogram"
        assert spec.buckets == buckets

    def test_metric_spec_gauge(self):
        """Test creating a gauge metric spec"""
        spec = MetricSpec(
            name="test_active_connections", type="gauge", description="Active connections"
        )

        assert spec.name == "test_active_connections"
        assert spec.type == "gauge"
        assert spec.labels == []
        assert spec.buckets is None


class TestPrometheusMetricsScenarioRegistration:
    """Tests for scenario metric registration in PrometheusMetrics adapter"""

    @pytest.fixture
    def metrics(self):
        """Create fresh PrometheusMetrics instance with isolated registry"""
        registry = CollectorRegistry()
        return PrometheusMetrics(registry=registry)

    def test_register_counter_metric(self, metrics):
        """Test registering a counter metric for a scenario"""
        metric_specs = [
            MetricSpec(
                name="scenario_test_operations_total",
                type="counter",
                description="Total test operations",
                labels=["operation_type"],
            )
        ]

        metrics.register_scenario_metrics("test-scenario", metric_specs)

        # Verify metric is registered
        assert "scenario_test_operations_total" in metrics._counters

        # Verify we can increment the counter
        metrics.increment_counter("scenario_test_operations_total", {"operation_type": "read"})

    def test_register_gauge_metric(self, metrics):
        """Test registering a gauge metric for a scenario"""
        metric_specs = [
            MetricSpec(
                name="scenario_test_active_requests",
                type="gauge",
                description="Active requests",
            )
        ]

        metrics.register_scenario_metrics("test-scenario", metric_specs)

        # Verify metric is registered
        assert "scenario_test_active_requests" in metrics._gauges

        # Verify we can set gauge value
        metrics.set_gauge("scenario_test_active_requests", 42.0)

    def test_register_histogram_metric(self, metrics):
        """Test registering a histogram metric for a scenario"""
        metric_specs = [
            MetricSpec(
                name="scenario_test_latency_seconds",
                type="histogram",
                description="Request latency",
                labels=["endpoint"],
            )
        ]

        metrics.register_scenario_metrics("test-scenario", metric_specs)

        # Verify metric is registered
        assert "scenario_test_latency_seconds" in metrics._histograms

        # Verify we can observe values
        metrics.observe_histogram("scenario_test_latency_seconds", 0.123, {"endpoint": "/api/test"})

    def test_register_histogram_with_custom_buckets(self, metrics):
        """Test registering histogram with custom buckets"""
        buckets = [1, 2, 5, 10, 20, 50, 100]
        metric_specs = [
            MetricSpec(
                name="scenario_test_query_count",
                type="histogram",
                description="Query count per request",
                buckets=buckets,
            )
        ]

        metrics.register_scenario_metrics("n-plus-one", metric_specs)

        assert "scenario_test_query_count" in metrics._histograms

    def test_register_multiple_metrics_for_scenario(self, metrics):
        """Test registering multiple metrics for a single scenario"""
        metric_specs = [
            MetricSpec(
                name="cache_hit_total", type="counter", description="Cache hits", labels=["cache_type"]
            ),
            MetricSpec(
                name="cache_miss_total", type="counter", description="Cache misses", labels=["cache_type"]
            ),
            MetricSpec(
                name="cache_hit_rate", type="gauge", description="Cache hit rate percentage"
            ),
        ]

        metrics.register_scenario_metrics("cache-stampede", metric_specs)

        assert "cache_hit_total" in metrics._counters
        assert "cache_miss_total" in metrics._counters
        assert "cache_hit_rate" in metrics._gauges

    def test_register_scenario_metrics_idempotent(self, metrics):
        """Test that registering the same scenario twice doesn't cause errors"""
        metric_specs = [
            MetricSpec(name="test_metric_total", type="counter", description="Test metric")
        ]

        # Register once
        metrics.register_scenario_metrics("test-scenario", metric_specs)
        assert "test_metric_total" in metrics._counters

        # Register again - should be no-op
        metrics.register_scenario_metrics("test-scenario", metric_specs)
        assert "test_metric_total" in metrics._counters

        # Verify scenario is tracked as registered
        assert "test-scenario" in metrics._registered_scenario_metrics

    def test_register_metrics_for_different_scenarios(self, metrics):
        """Test registering metrics for multiple different scenarios"""
        cache_metrics = [
            MetricSpec(name="cache_operations_total", type="counter", description="Cache operations")
        ]

        db_metrics = [
            MetricSpec(
                name="db_queries_per_request",
                type="histogram",
                description="DB queries per request",
                buckets=[1, 2, 5, 10, 20, 50],
            )
        ]

        metrics.register_scenario_metrics("cache-stampede", cache_metrics)
        metrics.register_scenario_metrics("n-plus-one-query", db_metrics)

        assert "cache_operations_total" in metrics._counters
        assert "db_queries_per_request" in metrics._histograms
        assert "cache-stampede" in metrics._registered_scenario_metrics
        assert "n-plus-one-query" in metrics._registered_scenario_metrics

    def test_skip_duplicate_metric_names(self, metrics):
        """Test that duplicate metric names across scenarios are skipped gracefully"""
        # Register first scenario with a metric
        metrics.register_scenario_metrics(
            "scenario-1",
            [MetricSpec(name="shared_metric_total", type="counter", description="Shared metric")],
        )

        # Try to register same metric name in different scenario - should skip gracefully
        metrics.register_scenario_metrics(
            "scenario-2",
            [MetricSpec(name="shared_metric_total", type="counter", description="Another metric")],
        )

        # Both scenarios should be marked as registered
        assert "scenario-1" in metrics._registered_scenario_metrics
        assert "scenario-2" in metrics._registered_scenario_metrics

        # Metric should only be registered once
        assert "shared_metric_total" in metrics._counters

    def test_get_metrics_includes_scenario_metrics(self, metrics):
        """Test that scenario metrics are included in the metrics output"""
        metric_specs = [
            MetricSpec(
                name="scenario_custom_metric_total",
                type="counter",
                description="Custom scenario metric",
            )
        ]

        metrics.register_scenario_metrics("test-scenario", metric_specs)
        metrics.increment_counter("scenario_custom_metric_total")

        # Get metrics in Prometheus format
        output = metrics.get_metrics().decode("utf-8")

        # Verify the metric appears in output
        assert "scenario_custom_metric_total" in output
        assert "Custom scenario metric" in output
