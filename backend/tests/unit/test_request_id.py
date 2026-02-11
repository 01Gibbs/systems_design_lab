import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

import uuid
from fastapi import FastAPI
from starlette.testclient import TestClient
from app.api.middleware.request_id import RequestIdMiddleware


def test_request_id_middleware_sets_header():
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    client = TestClient(app)
    response = client.get("/ping")
    # Should always set X-Request-ID header
    assert "X-Request-ID" in response.headers
    # Should be a valid UUID
    uuid.UUID(response.headers["X-Request-ID"])

    # If client sends X-Request-ID, it should be preserved
    custom_id = str(uuid.uuid4())
    response2 = client.get("/ping", headers={"X-Request-ID": custom_id})
    assert response2.headers["X-Request-ID"] == custom_id
