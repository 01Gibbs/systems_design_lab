"""Test SimulatorService for scenario management logic"""
import pytest
from datetime import datetime, timedelta
from app.application.simulator.service import SimulatorService
from app.application.simulator.models import ActiveScenarioState
from app.contracts.simulator import (
    EnableScenarioRequest, DisableScenarioRequest
)

class DummyClock:
    def __init__(self, now=None):
        self._now = now or datetime(2026, 2, 11, 12, 0, 0)
    def now(self):
        return self._now

class DummyStore:
    def __init__(self):
        self._active = []
        self._removed = []
        self._cleared = False
    def list_active(self):
        return list(self._active)
    def upsert(self, state):
        self._active = [s for s in self._active if s.name != state.name] + [state]
    def remove(self, name):
        self._active = [s for s in self._active if s.name != name]
        self._removed.append(name)
    def clear(self):
        self._active = []
        self._cleared = True

class DummyScenario:
    def __init__(self, name="foo"): self.meta = type("Meta", (), {"name": name, "description": "desc", "targets": ["http"], "parameter_schema": {}, "safety_limits": {}})()
    def is_applicable(self, *, target): return True
    def apply(self, *, ctx, parameters): return {}

class DummyRegistry:
    def __init__(self, scenarios): self._scenarios = scenarios
    @property
    def scenarios(self): return self._scenarios
    def get(self, name): return self._scenarios[name]

def make_service(now=None, expired=False):
    clock = DummyClock(now)
    store = DummyStore()
    reg = DummyRegistry({"foo": DummyScenario("foo")})
    svc = SimulatorService(store=store, clock=clock, registry=reg)
    # Add an active scenario
    enabled_at = clock.now() - timedelta(seconds=20)
    expires_at = clock.now() - timedelta(seconds=10) if expired else clock.now() + timedelta(seconds=10)
    store._active.append(ActiveScenarioState(name="foo", parameters={"x": 1}, enabled_at=enabled_at, expires_at=expires_at))
    return svc, store, clock

def test_list_scenarios():
    svc, *_ = make_service()
    out = svc.list_scenarios()
    assert out.scenarios[0].name == "foo"

def test_status_removes_expired():
    svc, store, _ = make_service(expired=True)
    out = svc.status()
    assert out.active == []
    assert store._removed == ["foo"]

def test_status_lists_active():
    svc, *_ = make_service()
    out = svc.status()
    assert out.active[0].name == "foo"
    assert out.active[0].parameters == {"x": 1}

def test_enable_and_disable():
    svc, store, _ = make_service()
    req = EnableScenarioRequest(name="foo", parameters={"y": 2}, duration_seconds=5)
    out = svc.enable(req)
    assert any(a.name == "foo" and a.parameters["y"] == 2 for a in out.active)
    req2 = DisableScenarioRequest(name="foo")
    out2 = svc.disable(req2)
    assert all(a.name != "foo" for a in out2.active)
    assert store._removed[-1] == "foo"

def test_reset():
    svc, store, _ = make_service()
    out = svc.reset()
    assert out.active == []
    assert store._cleared
