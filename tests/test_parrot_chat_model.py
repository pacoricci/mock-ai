from mock_ai.models.parrot_chat import ParrotChatModel
from mock_ai.schemas.chat_completion_request import ModelSettings


def test_parrot_chat_simple():
    model = ParrotChatModel()
    settings = ModelSettings(messages=[{"role": "user", "content": "ciao"}])
    resp = model.get_response(settings, False)
    assert resp.choices[0].message.content == "ciao"


def test_parrot_chat_stream():
    model = ParrotChatModel()
    settings = ModelSettings(messages=[{"role": "user", "content": "hola"}])
    chunks = list(model.get_response(settings, True))
    content = "".join(c.choices[0].delta.content or "" for c in chunks)
    assert content == "hola"
