import sys
import types

# Stub external dependencies not installed in test env
if "numpy" not in sys.modules:

    def _dummy_randint(*args, **kwargs):
        class Arr:
            def tolist(self):
                return []

        return Arr()

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

from collections.abc import Iterator

import pytest
from pydantic import BaseModel

from mock_ai.utils import SSEEncoder


class DummyModel(BaseModel):
    foo: str


def test_sse_encoder_strings():
    values = ["first", "second", "third"]
    encoder = SSEEncoder(iter(values))
    results = [next(encoder) for _ in values]
    assert results == [f"data: {v}\n\n".encode() for v in values]


def test_sse_encoder_dicts():
    values = [{"a": 1}, {"b": 2}]
    encoder = SSEEncoder(iter(values))
    results = [next(encoder) for _ in values]
    assert results == [f"data: {v}\n\n".encode() for v in values]


def test_sse_encoder_models():
    values = [DummyModel(foo="bar"), DummyModel(foo="baz")]
    encoder = SSEEncoder(iter(values))
    results = [next(encoder) for _ in values]
    expected = [
        f"data: {item.model_dump_json()}\n\n".encode() for item in values
    ]
    assert results == expected


def test_sse_encoder_unsupported_type():
    class Bad:
        pass

    iterator: Iterator[object] = iter([Bad()])
    encoder = SSEEncoder(iterator)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        next(encoder)
