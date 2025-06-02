import sys
from collections.abc import Iterator

import pytest
from pydantic import BaseModel

from mock_ai.utils import (
    SSEEncoder,
    Token,
    TokenBatchFactory,
    check_image_id,
    gen_image_id,
    get_data_from_image_id,
    parse_dimensions,
)


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


def test_parse_dimensions():
    assert parse_dimensions("640x480") == (640, 480)


def test_parse_dimensions_error():
    with pytest.raises(ValueError):
        parse_dimensions("640*480")


def test_image_id_round_trip_and_validation():
    payload = "640x480|PNG"
    img_id = gen_image_id(payload)
    assert check_image_id(img_id)
    assert get_data_from_image_id(img_id) == payload

    invalid_id = img_id[:-1] + ("0" if img_id[-1] != "0" else "1")
    assert not check_image_id(invalid_id)
    assert get_data_from_image_id(invalid_id) is None


def test_token_and_batch(monkeypatch):
    token = Token(n=15)
    assert len(token) == 15
    assert token[0] == "[0]\n"
    assert token[10] == "[10] "
    with pytest.raises(IndexError):
        _ = token[15]

    class Arr:
        def __init__(self, vals):
            self._vals = vals

        def tolist(self):
            return self._vals

    def fake_randint(_low, _high=None, size=None):
        return Arr(list(range(size or 1)))

    monkeypatch.setattr(sys.modules["numpy"].random, "randint", fake_randint)

    batch = TokenBatchFactory(batch_size=3, n=15, stop_token=99)
    out = next(batch)
    assert out == "[0]\n[1][2]"
    assert len(batch) == 3

    batch *= 2

    out2 = next(batch)
    expected = "".join(token[i] for i in range(6))
    assert out2 == expected
    assert len(batch) == 6
