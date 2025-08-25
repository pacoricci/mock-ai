import os

from fastapi.testclient import TestClient

from mock_ai.app import api_app
from mock_ai.settings import auth_settings


def test_cors_headers(monkeypatch):
    # ensure token is accepted
    monkeypatch.setattr(auth_settings, "bearer_tokens", ["token"])
    client = TestClient(api_app)
    response = client.get(
        "/v1/models/",
        headers={
            "Authorization": "Bearer token",
            "Origin": "http://example.com",
        },
    )
    assert response.headers.get("Access-Control-Allow-Origin") == "*"


def test_cors_headers_no_auth(monkeypatch):
    # ensure token is accepted
    monkeypatch.setattr(auth_settings, "bearer_tokens", None)
    client = TestClient(api_app)
    response = client.get(
        "/v1/models/",
        headers={
            "Origin": "http://example.com",
        },
    )
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
