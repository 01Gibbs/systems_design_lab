import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Disable OpenTelemetry during tests to prevent hanging on shutdown
os.environ["OTEL_SDK_DISABLED"] = "true"

import pytest
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY
from app.api.main import create_app


@pytest.fixture(scope="module")
def test_client():
    """Provide a FastAPI TestClient for integration tests

    Using module scope to avoid re-registering Prometheus metrics
    for each test function, which causes 'Duplicated timeseries' errors.
    """
    # Clear any existing metrics from previous test modules
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        try:
            REGISTRY.unregister(collector)
        except Exception:
            pass

    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def reset_simulator(test_client):
    """Reset simulator state before each test to prevent interference"""
    # Reset before test
    test_client.post("/api/sim/reset")
    yield
    # Reset after test (cleanup)
    test_client.post("/api/sim/reset")
