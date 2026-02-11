import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

import pytest
from fastapi import FastAPI, Response
from starlette.testclient import TestClient
from app.api.middleware.simulator_injection import SimulatorInjectionMiddleware

class DummySimService:
    def __init__(self, status_return):
        self._status_return = status_return
    def status(self):
        return self._status_return

class DummyActive:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

class DummyScenario:
    def __init__(self, effects):
        self.meta = type('Meta', (), {'name': 'dummy'})
        self._effects = effects
    def is_applicable(self, *, target):
        return True
    def apply(self, *, ctx, parameters):
        return self._effects

class DummyRegistry:
    def __init__(self, scenario):
        self._scenario = scenario
    def get(self, name):
        return self._scenario

@pytest.mark.parametrize("effects,expected_status,expected_delay", [
    ({}, 200, 0),
    ({"http_force_error": True}, 500, 0),
    ({"http_delay_ms": 50}, 200, 0.04),
])
def test_simulator_injection_effects(effects, expected_status, expected_delay):
    app = FastAPI()
    scenario = DummyScenario(effects)
    registry = DummyRegistry(scenario)
    sim_service = DummySimService(type('Status', (), {'active': [DummyActive('dummy', {})]})())
    sim_service._registry = registry
    app.state.simulator_service = sim_service
    app.add_middleware(SimulatorInjectionMiddleware)

    @app.get("/test")
    async def test():
        return {"ok": True}

    client = TestClient(app)
    start = time.time()
    resp = client.get("/test")
    elapsed = time.time() - start
    assert resp.status_code == expected_status
    if effects.get("http_delay_ms"):
        assert elapsed >= expected_delay

def test_simulator_injection_handles_exception():
    app = FastAPI()
    scenario = DummyScenario({})
    registry = DummyRegistry(scenario)
    sim_service = DummySimService(type('Status', (), {'active': [DummyActive('dummy', {})]})())
    sim_service._registry = registry
    app.state.simulator_service = sim_service
    app.add_middleware(SimulatorInjectionMiddleware)

    @app.get("/fail")
    async def fail():
        raise RuntimeError("fail")

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/fail")
    assert resp.status_code == 500
