"""Test ScenarioRegistry for registration and lookup"""
from app.application.simulator.registry import ScenarioRegistry, Scenario
from app.application.simulator.models import ScenarioMeta
import pytest

class DummyScenario:
    def __init__(self, name="dummy", desc="desc"):
        self.meta = ScenarioMeta(
            name=name,
            description=desc,
            targets=["http"],
            parameter_schema={},
            safety_limits={},
        )
    def is_applicable(self, *, target):
        return True
    def apply(self, *, ctx, parameters):
        return {"effect": True}

def test_registry_get_and_list():
    s1 = DummyScenario("foo")
    s2 = DummyScenario("bar")
    reg = ScenarioRegistry({s1.meta.name: s1, s2.meta.name: s2})
    # List
    scenarios = reg.scenarios
    assert set(scenarios.keys()) == {"foo", "bar"}
    # Get
    assert reg.get("foo") is s1
    assert reg.get("bar") is s2

def test_registry_get_missing():
    reg = ScenarioRegistry({})
    with pytest.raises(KeyError) as e:
        reg.get("nope")
    assert "Unknown scenario" in str(e.value)
