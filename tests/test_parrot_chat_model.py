import asyncio

import pytest

from mock_ai.models.chat.parrot_chat import ParrotChatModel
from mock_ai.schemas.chat_completion_request import ModelSettings


@pytest.mark.asyncio
async def test_parrot_chat_simple():
    model = ParrotChatModel()
    settings = ModelSettings(messages=[{"role": "user", "content": "ciao"}])
    resp = await model.get_response(settings, False)
    assert resp.choices[0].message.content == "ciao"


@pytest.mark.asyncio
async def test_parrot_chat_stream():
    model = ParrotChatModel()
    settings = ModelSettings(messages=[{"role": "user", "content": "hola"}])
    chunks = await model.get_response(settings, True)

    content = "".join([c.choices[0].delta.content or "" async for c in chunks])
    assert content == "hola"
