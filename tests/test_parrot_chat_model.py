import sys
import types

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
