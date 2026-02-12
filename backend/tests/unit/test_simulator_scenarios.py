"""Test all scenario classes for effect dicts and applicability"""
import pytest
from app.application.simulator.scenarios.algorithmic_degradation import AlgorithmicDegradation
from app.application.simulator.scenarios.cache_stampede import CacheStampede
from app.application.simulator.scenarios.circuit_breaker import CircuitBreaker
from app.application.simulator.scenarios.connection_pool_exhaustion import (
    ConnectionPoolExhaustion,
)
from app.application.simulator.scenarios.error_burst import ErrorBurst
from app.application.simulator.scenarios.fixed_latency import FixedLatency
from app.application.simulator.scenarios.lock_contention import LockContention
from app.application.simulator.scenarios.retry_storm import RetryStorm
from app.application.simulator.scenarios.slow_db_query import SlowDbQuery

# AlgorithmicDegradation
ALG = AlgorithmicDegradation()
def test_algorithmic_degradation_apply_and_applicable():
    assert ALG.is_applicable(target={"category": "algorithm"})
    out = ALG.apply(ctx={}, parameters={"use_slow_path": True, "input_size": 123})
    assert out["algorithm_use_slow"] is True
    assert out["algorithm_input_size"] == 123
    out2 = ALG.apply(ctx={}, parameters={"use_slow_path": False})
    assert out2["algorithm_use_slow"] is False
    assert out2["algorithm_input_size"] == 100

# ErrorBurst
EB = ErrorBurst()
def test_error_burst_apply_and_applicable(monkeypatch):
    assert EB.is_applicable(target={"category": "http"})
    # Always return 0.0 for random.random to force error
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = EB.apply(ctx={}, parameters={"probability": 1.0})
    assert out == {"http_force_error": True, "http_path_prefix": "", "http_method": ""}
    # Always return 1.0 for random.random to avoid error
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = EB.apply(ctx={}, parameters={"probability": 0.5})
    assert out2 == {}

# FixedLatency
FL = FixedLatency()
def test_fixed_latency_apply_and_applicable(monkeypatch):
    assert FL.is_applicable(target={"category": "http"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = FL.apply(ctx={}, parameters={"ms": 100, "probability": 1.0})
    assert out["http_delay_ms"] == 100
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = FL.apply(ctx={}, parameters={"ms": 100, "probability": 0.5})
    assert out2 == {}

# LockContention
LC = LockContention()
def test_lock_contention_apply_and_applicable():
    assert LC.is_applicable(target={"category": "db"})
    out = LC.apply(ctx={}, parameters={"row_id": 5, "update_count": 3})
    assert out["db_lock_contention"] is True
    assert out["db_target_row_id"] == 5
    assert out["db_concurrent_updates"] == 3

# SlowDbQuery
SDQ = SlowDbQuery()
def test_slow_db_query_apply_and_applicable(monkeypatch):
    assert SDQ.is_applicable(target={"category": "db"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = SDQ.apply(ctx={}, parameters={"seconds": 1.5, "probability": 1.0})
    assert out["db_sleep_seconds"] == 1.5
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = SDQ.apply(ctx={}, parameters={"seconds": 1.5, "probability": 0.5})
    assert out2 == {}


# CircuitBreaker
CB = CircuitBreaker()
def test_circuit_breaker_apply_and_applicable(monkeypatch):
    assert CB.is_applicable(target={"category": "http"})
    # Force circuit open
    monkeypatch.setattr("random.random", lambda: 0.1)
    out = CB.apply(ctx={}, parameters={"failure_threshold": 5, "timeout_ms": 3000, "status_code": 503})
    assert out["circuit_breaker_open"] is True
    assert out["http_status"] == 503
    assert out["http_delay_ms"] == 3000
    # Circuit closed
    monkeypatch.setattr("random.random", lambda: 0.5)
    out2 = CB.apply(ctx={}, parameters={"failure_threshold": 5})
    assert out2 == {}


# RetryStorm
RS = RetryStorm()
def test_retry_storm_apply_and_applicable(monkeypatch):
    assert RS.is_applicable(target={"category": "http"})
    # Force failure
    monkeypatch.setattr("random.random", lambda: 0.1)
    out = RS.apply(ctx={}, parameters={"failure_rate": 0.5, "retry_multiplier": 3.0, "status_code": 503})
    assert out["retry_storm_active"] is True
    assert out["http_status"] == 503
    assert out["retry_multiplier"] == 3.0
    # No failure
    monkeypatch.setattr("random.random", lambda: 0.9)
    out2 = RS.apply(ctx={}, parameters={"failure_rate": 0.5})
    assert out2 == {}


# ConnectionPoolExhaustion
CPE = ConnectionPoolExhaustion()
def test_connection_pool_exhaustion_apply_and_applicable(monkeypatch):
    assert CPE.is_applicable(target={"category": "database"})
    # Force exhaustion
    monkeypatch.setattr("random.random", lambda: 0.1)
    out = CPE.apply(ctx={}, parameters={"exhaustion_probability": 0.8, "hang_duration_ms": 5000, "pool_size_limit": 20})
    assert out["db_connection_exhausted"] is True
    assert out["db_hang_duration_ms"] == 5000
    assert out["db_pool_size_limit"] == 20
    # No exhaustion
    monkeypatch.setattr("random.random", lambda: 0.9)
    out2 = CPE.apply(ctx={}, parameters={"exhaustion_probability": 0.5})
    assert out2 == {}


# CacheStampede
CS = CacheStampede()
def test_cache_stampede_apply_and_applicable(monkeypatch):
    assert CS.is_applicable(target={"category": "cache"})
    assert CS.is_applicable(target={"category": "database"})
    # Force stampede
    monkeypatch.setattr("random.random", lambda: 0.1)
    out = CS.apply(ctx={}, parameters={"stampede_probability": 0.8, "concurrent_requests": 100, "backend_delay_ms": 3000})
    assert out["cache_stampede_active"] is True
    assert out["cache_miss"] is True
    assert out["concurrent_backend_requests"] == 100
    assert out["db_query_delay_ms"] == 3000
    # No stampede
    monkeypatch.setattr("random.random", lambda: 0.9)
    out2 = CS.apply(ctx={}, parameters={"stampede_probability": 0.5})
    assert out2 == {}
