"""Test InMemorySimulatorStore for all CRUD operations"""
from app.infrastructure.simulator.memory_store import InMemorySimulatorStore
from app.application.simulator.models import ActiveScenarioState
from datetime import datetime, timedelta

def make_state(name, params=None):
    return ActiveScenarioState(
        name=name,
        parameters=params or {},
        enabled_at=datetime(2026, 2, 11, 12, 0, 0),
        expires_at=datetime(2026, 2, 11, 13, 0, 0),
    )

def test_upsert_and_list_and_get():
    store = InMemorySimulatorStore()
    s1 = make_state("foo", {"x": 1})
    s2 = make_state("bar", {"y": 2})
    store.upsert(s1)
    store.upsert(s2)
    active = store.list_active()
    assert set(a.name for a in active) == {"foo", "bar"}
    assert store.get("foo").parameters["x"] == 1
    assert store.get("bar").parameters["y"] == 2

def test_remove():
    store = InMemorySimulatorStore()
    s1 = make_state("foo")
    store.upsert(s1)
    store.remove("foo")
    assert store.get("foo") is None
    assert store.list_active() == []

def test_clear():
    store = InMemorySimulatorStore()
    store.upsert(make_state("foo"))
    store.upsert(make_state("bar"))
    store.clear()
    assert store.list_active() == []
    assert store.get("foo") is None
    assert store.get("bar") is None
