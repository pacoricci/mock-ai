import asyncio
import sys
import types

from mock_ai import utils
from mock_ai.app import (
    chat_completions,
    embeddings,
    images_generations,
    model as model_endpoint,
    models as models_endpoint,
    private,
)
from mock_ai.models.standard_registry import STANDARD_REGISTRY
from mock_ai.schemas.chat_completion_request import ChatCompletionRequest
from mock_ai.schemas.embedding_request import EmbeddingRequest
from mock_ai.schemas.embedding_response import (
    EmbeddingObject,
    EmbeddingResponse,
)
from mock_ai.schemas.image_request import ImageRequest
from mock_ai.schemas.usage import Usage


def run(coro):
    return asyncio.run(coro)


def test_models_list_and_detail():
    resp = run(models_endpoint())
    assert resp.object == "list"
    assert len(resp.data) >= 1

    model_id = resp.data[0].id
    detail = run(model_endpoint(model_id))
    assert detail.id == model_id

    try:
        run(model_endpoint("unknown"))
    except Exception as e:
        assert getattr(e, "status_code", None) == 404


def test_chat_completion_non_stream():
    payload = ChatCompletionRequest(
        model="mock-chat-model", messages=[{"role": "user", "content": "hi"}]
    )
    response = run(chat_completions(payload))
    assert response.media_type == "application/json"


def test_embeddings(monkeypatch):
    model = STANDARD_REGISTRY.get("mock-embedding-model")

    def fake_get_response(_data):
        return EmbeddingResponse(
            data=[EmbeddingObject(index=0, embedding=[1.0, 2.0, 3.0])],
            model="test",
            usage=Usage(prompt_tokens=1, completion_tokens=0),
        )

    monkeypatch.setattr(model, "get_response", fake_get_response)
    req = EmbeddingRequest(model="mock-embedding-model", input="hello")
    resp = run(embeddings(req))
    assert resp.data[0].embedding == [1.0, 2.0, 3.0]


def test_image_generation_url():
    req = ImageRequest(
        model="mock-image-model", prompt="x", response_format="url"
    )
    resp = run(
        images_generations(req, types.SimpleNamespace(base_url="http://test/"))
    )
    assert resp.data
    assert resp.data[0].url.startswith("http://test/")


def test_private_image_endpoint(monkeypatch):
    class DummyImage:
        def save(self, buf, format=None):
            buf.write(b"dummy")

    monkeypatch.setattr(
        sys.modules["mock_ai.app"],
        "generate_noise_image_from_string",
        lambda *a, **k: DummyImage(),
    )
    img_id = utils.gen_image_id("10x10|PNG")
    response = run(private(img_id, "png"))
    assert response.media_type == "image/png"
