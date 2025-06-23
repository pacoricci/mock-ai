import os

from fastapi.testclient import TestClient

from mock_ai.app import app
from mock_ai.settings import auth_settings


def test_cors_headers(monkeypatch):
    # ensure token is accepted
    monkeypatch.setattr(auth_settings, "bearer_tokens", ["token"])
    client = TestClient(app)
    response = client.get(
        "/v1/models/",
        headers={
            "Authorization": "Bearer token",
            "Origin": "http://example.com",
        },
    )
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
