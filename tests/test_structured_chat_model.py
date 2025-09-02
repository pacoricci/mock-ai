import asyncio
import json

import pytest

from mock_ai.models.chat.structured_chat import StructuredChatModel
from mock_ai.schemas.chat_completion_request import ModelSettings


@pytest.mark.asyncio
async def test_structured_chat_json_object():
    model = StructuredChatModel()
    settings = ModelSettings(
        messages=[{"role": "user", "content": "ciao"}],
        response_format={"type": "json_object"},
    )
    resp = await model.get_response(settings, False)
    data = json.loads(resp.choices[0].message.content)
    assert isinstance(data, dict)


async def async_noop(*args, **kwargs):
    pass


@pytest.mark.asyncio
async def test_structured_chat_json_schema_stream(monkeypatch):
    monkeypatch.setattr(
        "mock_ai.models.chat.structured_chat.asyncio.sleep", async_noop
    )
    model = StructuredChatModel()
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }
    settings = ModelSettings(
        messages=[{"role": "user", "content": "foo"}],
        response_format={"type": "json_schema", "json_schema": schema},
    )
    chunks = []
    async for chunk in await model.get_response(settings, True):
        chunks.append(chunk)
    content = "".join(c.choices[0].delta.content or "" for c in chunks)
    data = json.loads(content)
    assert set(data.keys()) == {"name", "age"}
