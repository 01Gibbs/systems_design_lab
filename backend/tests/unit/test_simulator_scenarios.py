# CpuSpike
from app.application.simulator.scenarios.cpu_spike import CpuSpike


def test_cpu_spike_apply_and_applicable(monkeypatch):
    cs = CpuSpike()
    assert cs.is_applicable(target={"category": "http"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = cs.apply(ctx={}, parameters={"spike_probability": 1.0, "duration_ms": 500})
    assert out["cpu_spike_ms"] == 500
    # No spike
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = cs.apply(ctx={}, parameters={"spike_probability": 0.0})
    assert out2 == {}


# MemoryLeak
from app.application.simulator.scenarios.memory_leak import MemoryLeak


def test_memory_leak_apply_and_applicable(monkeypatch):
    ml = MemoryLeak()
    assert ml.is_applicable(target={"category": "db"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = ml.apply(ctx={}, parameters={"leak_probability": 1.0, "leak_size_kb": 256})
    assert out["memory_leak_kb"] == 256
    # No leak
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = ml.apply(ctx={}, parameters={"leak_probability": 0.0})
    assert out2 == {}


# DiskFull
from app.application.simulator.scenarios.disk_full import DiskFull


def test_disk_full_apply_and_applicable(monkeypatch):
    df = DiskFull()
    assert df.is_applicable(target={"category": "db"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = df.apply(ctx={}, parameters={"failure_probability": 1.0, "path_prefix": "/tmp"})
    assert out["disk_full_error"] is True
    assert out["path_prefix"] == "/tmp"
    # No failure
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = df.apply(ctx={}, parameters={"failure_probability": 0.0})
    assert out2 == {}


# NetworkPartition
from app.application.simulator.scenarios.network_partition import NetworkPartition


def test_network_partition_apply_and_applicable(monkeypatch):
    np = NetworkPartition()
    assert np.is_applicable(target={"category": "http"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = np.apply(ctx={}, parameters={"partition_probability": 1.0, "delay_ms": 200, "drop": True})
    assert out["network_partition"] is True
    assert out["delay_ms"] == 200
    assert out["drop_request"] is True
    # No partition
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = np.apply(ctx={}, parameters={"partition_probability": 0.0})
    assert out2 == {}


# ClockSkew
from app.application.simulator.scenarios.clock_skew import ClockSkew


def test_clock_skew_apply_and_applicable(monkeypatch):
    cs = ClockSkew()
    assert cs.is_applicable(target={"category": "time"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = cs.apply(ctx={}, parameters={"skew_probability": 1.0, "skew_ms": -5000})
    assert out["clock_skew_ms"] == -5000
    # No skew
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = cs.apply(ctx={}, parameters={"skew_probability": 0.0})
    assert out2 == {}


# ResourceStarvation
from app.application.simulator.scenarios.resource_starvation import ResourceStarvation


def test_resource_starvation_apply_and_applicable(monkeypatch):
    rs = ResourceStarvation()
    assert rs.is_applicable(target={"category": "database"})
    monkeypatch.setattr("random.random", lambda: 0.0)
    out = rs.apply(ctx={}, parameters={"starvation_probability": 1.0, "max_workers": 3})
    assert out["resource_starvation"] is True
    assert out["max_workers"] == 3
    # No starvation
    monkeypatch.setattr("random.random", lambda: 1.0)
    out2 = rs.apply(ctx={}, parameters={"starvation_probability": 0.0})
    assert out2 == {}


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
    assert out == {
        "http_force_error": True,
        "http_path_prefix": "",
        "http_method": "",
        "scenario_name": "error-burst-5xx",
    }
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
    out = CB.apply(
        ctx={}, parameters={"failure_threshold": 5, "timeout_ms": 3000, "status_code": 503}
    )
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
    out = RS.apply(
        ctx={}, parameters={"failure_rate": 0.5, "retry_multiplier": 3.0, "status_code": 503}
    )
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
    assert CPE.is_applicable(target={"category": "db"})
    # Force exhaustion
    monkeypatch.setattr("random.random", lambda: 0.1)
    out = CPE.apply(
        ctx={},
        parameters={"exhaustion_probability": 0.8, "hang_duration_ms": 5000, "pool_size_limit": 20},
    )
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
    assert CS.is_applicable(target={"category": "db"})
    # Force stampede
    monkeypatch.setattr("random.random", lambda: 0.1)
    out = CS.apply(
        ctx={},
        parameters={
            "stampede_probability": 0.8,
            "concurrent_requests": 100,
            "backend_delay_ms": 3000,
        },
    )
    assert out["cache_stampede_active"] is True
    assert out["cache_miss"] is True
    assert out["concurrent_backend_requests"] == 100
    assert out["db_query_delay_ms"] == 3000
    # No stampede
    monkeypatch.setattr("random.random", lambda: 0.9)
    out2 = CS.apply(ctx={}, parameters={"stampede_probability": 0.5})
    assert out2 == {}
