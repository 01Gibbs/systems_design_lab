"""Unit tests for N+1 Query scenario"""

import pytest
from app.application.simulator.scenarios.n_plus_one_query import NPlusOneQuery


class DummyCounter:
    """Mock Counter for testing"""

    def __init__(self):
        self.count = 0
        self.labels_args = None

    def labels(self, **kwargs):
        self.labels_args = kwargs
        return self

    def inc(self, amount=1):
        self.count += amount


class DummyHistogram:
    """Mock Histogram for testing"""

    def __init__(self):
        self.observations = []
        self.labels_args = None

    def labels(self, **kwargs):
        self.labels_args = kwargs
        return self

    def observe(self, value):
        self.observations.append(value)


@pytest.mark.parametrize(
    "probability,n_items,expected_pattern",
    [
        (1.0, 10, "n_plus_one"),  # Always triggers N+1
        (0.0, 10, "optimized"),  # Never triggers N+1
    ],
)
def test_n_plus_one_query_pattern(probability, n_items, expected_pattern, monkeypatch):
    """Test that N+1 pattern triggers based on probability"""
    scenario = NPlusOneQuery()
    monkeypatch.setattr("random.random", lambda: 0.5)

    metrics = {
        "db_queries_per_request": DummyHistogram(),
        "db_query_count_total": DummyCounter(),
        "n_plus_one_detected_total": DummyCounter(),
    }
    ctx = {"metrics": metrics}
    params = {
        "n_items": n_items,
        "extra_query_delay_ms": 10,
        "probability": probability,
    }

    result = scenario.apply(ctx=ctx, parameters=params)

    assert result["pattern"] == expected_pattern
    if expected_pattern == "n_plus_one":
        assert result["is_n_plus_one"] is True
        assert result["db_query_count"] == 1 + n_items  # 1 + N queries
        assert result["db_delay_ms"] == 10 * n_items
        assert metrics["n_plus_one_detected_total"].count == 1
        assert metrics["db_queries_per_request"].observations == [1 + n_items]
    else:
        assert result["is_n_plus_one"] is False
        assert result["db_query_count"] == 1  # Optimized: 1 query
        assert result["db_delay_ms"] == 0
        assert metrics["n_plus_one_detected_total"].count == 0
        assert metrics["db_queries_per_request"].observations == [1]


def test_n_plus_one_query_metrics_incremented():
    """Test that metrics are correctly incremented"""
    scenario = NPlusOneQuery()

    metrics = {
        "db_queries_per_request": DummyHistogram(),
        "db_query_count_total": DummyCounter(),
        "n_plus_one_detected_total": DummyCounter(),
    }
    ctx = {"metrics": metrics}
    params = {"n_items": 5, "extra_query_delay_ms": 20, "probability": 1.0}

    result = scenario.apply(ctx=ctx, parameters=params)

    # Verify histogram observation
    assert len(metrics["db_queries_per_request"].observations) == 1
    assert metrics["db_queries_per_request"].observations[0] == 6  # 1 + 5

    # Verify counter increment (6 queries total)
    assert metrics["db_query_count_total"].count == 6

    # Verify N+1 detection counter
    assert metrics["n_plus_one_detected_total"].count == 1


def test_n_plus_one_query_is_applicable():
    """Test that scenario only applies to DB targets"""
    scenario = NPlusOneQuery()

    assert scenario.is_applicable(target={"category": "db"}) is True
    assert scenario.is_applicable(target={"category": "http"}) is False
    assert scenario.is_applicable(target={"category": "cpu"}) is False
    assert scenario.is_applicable(target={}) is False


def test_n_plus_one_query_scenario_meta():
    """Test scenario metadata is correctly defined"""
    scenario = NPlusOneQuery()

    assert scenario.meta.name == "n-plus-one-query"
    assert "db" in scenario.meta.targets
    assert "n_items" in scenario.meta.parameter_schema
    assert "probability" in scenario.meta.parameter_schema
    assert len(scenario.meta.metrics) == 3
    assert scenario.meta.metrics[0].name == "db_queries_per_request"
    assert scenario.meta.metrics[0].type == "histogram"
    assert scenario.meta.metrics[1].name == "db_query_count_total"
    assert scenario.meta.metrics[2].name == "n_plus_one_detected_total"
