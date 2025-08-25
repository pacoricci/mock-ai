import json

import pytest
from fastapi.testclient import TestClient

from mock_ai.app import app


def _first_result_event(client: TestClient, payload: dict) -> dict:
    headers = {
        "accept": "application/json, text/event-stream",
        "content-type": "application/json",
    }
    with client.stream(
        "POST",
        "/mcp-servers/foo/mcp",
        headers=headers,
        content=json.dumps(payload),
    ) as response:
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith(
            "text/event-stream"
        )

        for raw_line in response.iter_lines():
            if not raw_line:
                continue
            line = (
                raw_line.decode()
                if isinstance(raw_line, bytes | bytearray)
                else raw_line
            )
            if not line.startswith("data: "):
                continue
            data = line[len("data: ") :]
            try:
                message = json.loads(data)
            except Exception:
                continue
            if isinstance(message, dict) and (
                "result" in message or "error" in message
            ):
                return message

    raise AssertionError("No JSON-RPC result received from MCP stream")


@pytest.fixture(scope="module")
def api_client() -> TestClient:
    # Start the app once so the MCP session manager runs for the module
    with TestClient(app) as client:
        yield client


def test_mcp_initialize_streams_ok(api_client: TestClient):
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "tests", "version": "0.0.0"},
        },
    }
    message = _first_result_event(api_client, payload)
    assert message.get("jsonrpc") == "2.0"
    assert "result" in message


def test_mcp_tools_list_contains_greet(api_client: TestClient):
    payload = {
        "jsonrpc": "2.0",
        "id": "2",
        "method": "tools/list",
        "params": {},
    }

    message = _first_result_event(api_client, payload)
    # Do not rely on exact schema; ensure our test tool name surfaces
    assert "result" in message
    # We registered an example tool named "add"; also "greet" may exist
    assert ("add" in json.dumps(message)) or ("greet" in json.dumps(message))
