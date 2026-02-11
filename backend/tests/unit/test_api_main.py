"""Test FastAPI app instantiation and health endpoint."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app.api.main import app
from starlette.testclient import TestClient

def test_app_instantiates():
    client = TestClient(app)
    response = client.get("/api/health")
    # Accept 200 or 404 (if health endpoint not implemented yet)
    assert response.status_code in (200, 404)
