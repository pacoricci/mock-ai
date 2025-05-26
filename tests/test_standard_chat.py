import json
import re
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.modules.pop("mock_ai", None)
sys.modules.pop("mock_ai.models", None)
sys.modules.pop("mock_ai.models.standard_chat", None)
sys.modules.pop("mock_ai.schemas", None)
sys.modules.pop("mock_ai.schemas.chat_completion_request", None)

if "numpy" not in sys.modules:

    def _dummy_randint(low=0, high=None, size=None, **kwargs):
        if isinstance(size, tuple):
            n = size[0]
        else:
            n = size or 1

        class Arr:
            def __init__(self, count: int) -> None:
                self.count = count

            def tolist(self):
                return list(range(1, self.count + 1))

        return Arr(n)

    mod = types.ModuleType("numpy")
    mod.random = types.SimpleNamespace(
        Generator=object,
        default_rng=lambda *a, **k: None,
        randint=_dummy_randint,
    )
    mod.linalg = types.SimpleNamespace(norm=lambda x: 1)
    mod.ndarray = object
    mod.uint8 = object
    sys.modules["numpy"] = mod
if "PIL" not in sys.modules:
    pil_mod = types.ModuleType("PIL")
    sys.modules["PIL"] = pil_mod
    image_mod = types.ModuleType("PIL.Image")
    image_mod.Image = object
    sys.modules["PIL.Image"] = image_mod

from mock_ai.models.standard_chat import StandardChatModel
from mock_ai.schemas.chat_completion_request import ModelSettings


def _count_tokens(text: str) -> int:
    return len(re.findall(r"\[\d+\]", text))


def test_standard_chat_non_stream():
    model = StandardChatModel("test", completions_tokens_limit=7)
    settings = ModelSettings(messages=[{"role": "user", "content": "hello"}])
    resp = model.get_response(settings, False)
    content = resp.choices[0].message.content
    assert _count_tokens(content) == 7
    assert resp.usage.prompt_tokens == 1
    assert resp.usage.completion_tokens == 1


def test_standard_chat_stream(monkeypatch):
    model = StandardChatModel("test", completions_tokens_limit=25)
    settings = ModelSettings(
        messages=[{"role": "user", "content": "hello"}],
        stream_options={"include_usage": True},
    )
    monkeypatch.setattr(
        "mock_ai.models.standard_chat.time.sleep", lambda *_: None
    )
    chunks = list(model.get_response(settings, True))

    delta_contents = [c.choices[0].delta.content for c in chunks if c.choices]
    token_counts = [_count_tokens(c) for c in delta_contents]

    assert sum(token_counts) == 25
    assert (
        len(delta_contents)
        == (25 + model.TOKEN_PER_BATCH - 1) // model.TOKEN_PER_BATCH
    )

    assert chunks[-1].choices == []
    assert chunks[-1].usage is not None


def test_standard_chat_json_object():
    model = StandardChatModel("test")
    settings = ModelSettings(
        messages=[{"role": "user", "content": "ciao"}],
        response_format={"type": "json_object"},
    )
    resp = model.get_response(settings, False)
    data = json.loads(resp.choices[0].message.content)
    assert isinstance(data, dict)


def test_standard_chat_json_schema_stream(monkeypatch):
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
        "mock_ai.models.standard_chat.time.sleep", lambda *_: None
    )
    chunks = list(model.get_response(settings, True))
    content = "".join(c.choices[0].delta.content or "" for c in chunks if c.choices)
    data = json.loads(content)
    assert set(data.keys()) == {"name", "age"}
    assert chunks[-1].usage is not None
