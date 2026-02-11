"""Test simulator API router endpoints"""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.api.routers import simulator
from app.contracts.simulator import (
    EnableScenarioRequest,
    DisableScenarioRequest,
    ScenariosResponse,
    StatusResponse,
)

class DummyService:
    def __init__(self):
        from app.contracts.simulator import ScenarioDescriptor
        self._scenarios = [
            ScenarioDescriptor(
                name="latency",
                description="Injects latency",
                targets=["http"],
                parameter_schema={},
                safety_limits={},
            )
        ]
        self._active = []
    def list_scenarios(self):
        return ScenariosResponse(scenarios=self._scenarios)
    def status(self):
        return StatusResponse(active=self._active)
    def enable(self, req):
        from app.contracts.simulator import ActiveScenario
        self._active.append(
            ActiveScenario(
                name=req.name,
                parameters=req.parameters,
                enabled_at=datetime.utcnow(),
                expires_at=None,
            )
        )
        return self.status()
    def disable(self, req):
        self._active = [a for a in self._active if a.name != req.name]
        return self.status()
    def reset(self):
        self._active = []
        return self.status()

def make_app():
    app = FastAPI()
    app.include_router(simulator.router, prefix="/api/sim")
    app.state.simulator_service = DummyService()
    return app

def test_list_scenarios():
    app = make_app()
    client = TestClient(app)
    resp = client.get("/api/sim/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert "scenarios" in data
    assert data["scenarios"][0]["name"] == "latency"

def test_status_empty():
    app = make_app()
    client = TestClient(app)
    resp = client.get("/api/sim/status")
    assert resp.status_code == 200
    assert resp.json()["active"] == []

def test_enable_and_disable():
    app = make_app()
    client = TestClient(app)
    enable_req = {"name": "latency", "parameters": {}, "duration_seconds": 10}
    resp = client.post("/api/sim/enable", json=enable_req)
    assert resp.status_code == 200
    assert len(resp.json()["active"]) == 1
    disable_req = {"name": "latency"}
    resp = client.post("/api/sim/disable", json=disable_req)
    assert resp.status_code == 200
    assert resp.json()["active"] == []

def test_reset():
    app = make_app()
    client = TestClient(app)
    enable_req = {"name": "latency", "parameters": {}, "duration_seconds": 10}
    client.post("/api/sim/enable", json=enable_req)
    resp = client.post("/api/sim/reset")
    assert resp.status_code == 200
    assert resp.json()["active"] == []
