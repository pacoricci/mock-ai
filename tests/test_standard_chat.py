import asyncio
import json
import re

import pytest

from mock_ai.models.chat.standard_chat import StandardChatModel
from mock_ai.schemas.chat_completion_request import ModelSettings


async def async_noop(*args, **kwargs):
    pass


def _count_tokens(text: str) -> int:
    return len(re.findall(r"\[\d+\]", text))


@pytest.mark.asyncio
async def test_standard_chat_non_stream():
    model = StandardChatModel("test", completions_tokens_limit=7)
    settings = ModelSettings(messages=[{"role": "user", "content": "hello"}])
    resp = await model.get_response(settings, False)
    content = resp.choices[0].message.content
    assert _count_tokens(content) <= 7
    assert resp.usage.prompt_tokens == 1
    assert resp.usage.completion_tokens == 1


@pytest.mark.asyncio
async def test_standard_chat_stream(monkeypatch):
    model = StandardChatModel("test", completions_tokens_limit=25)
    settings = ModelSettings(
        messages=[{"role": "user", "content": "hello"}],
        stream_options={"include_usage": True},
    )
    monkeypatch.setattr(
        "mock_ai.models.chat.standard_chat.asyncio.sleep", async_noop
    )
    chunks = []
    async for chunk in await model.get_response(settings, True):
        chunks.append(chunk)

    delta_contents = [c.choices[0].delta.content for c in chunks if c.choices]
    token_counts = [_count_tokens(c) for c in delta_contents]

    assert sum(token_counts) <= 25
    assert (
        len(delta_contents)
        == (25 + model.TOKEN_PER_BATCH - 1) // model.TOKEN_PER_BATCH
    )

    assert chunks[-1].choices == []
    assert chunks[-1].usage is not None


@pytest.mark.asyncio
async def test_standard_chat_json_object():
    model = StandardChatModel("test")
    settings = ModelSettings(
        messages=[{"role": "user", "content": "ciao"}],
        response_format={"type": "json_object"},
    )
    resp = await model.get_response(settings, False)
    data = json.loads(resp.choices[0].message.content)
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_standard_chat_json_schema_stream(monkeypatch):
    model = StandardChatModel("test")
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }
    settings = ModelSettings(
        messages=[{"role": "user", "content": "hi"}],
        response_format={"type": "json_schema", "json_schema": schema},
        stream_options={"include_usage": True},
    )
    monkeypatch.setattr(
        "mock_ai.models.chat.standard_chat.asyncio.sleep", async_noop
    )
    chunks = []
    async for chunk in await model.get_response(settings, True):
        chunks.append(chunk)
    content = "".join(
        c.choices[0].delta.content or "" for c in chunks if c.choices
    )
    data = json.loads(content)
    assert set(data.keys()) == {"name", "age"}
    assert chunks[-1].usage is not None
