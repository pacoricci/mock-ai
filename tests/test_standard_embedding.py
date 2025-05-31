import sys
import types
from pathlib import Path

# Ensure project root is on path and previous imports are cleared
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
for name in [
    "mock_ai",
    "mock_ai.models",
    "mock_ai.models.standard_embedding",
    "mock_ai.schemas",
    "mock_ai.schemas.embedding_request",
    "mock_ai.schemas.embedding_response",
    "mock_ai.utils",
]:
    sys.modules.pop(name, None)

class DummyArray(list):
    def __truediv__(self, other):
        return DummyArray([v/other for v in self])
    def tolist(self):
        return list(self)

class DummyRNG:
    def normal(self, loc: float = 0.0, scale: float = 1.0, size=None):
        n = size[0] if isinstance(size, tuple) else (size or 1)
        return DummyArray(list(range(n)))

def default_rng(*_a, **_k):
    return DummyRNG()

numpy_stub = types.ModuleType("numpy")
numpy_stub.random = types.SimpleNamespace(
    Generator=DummyRNG,
    default_rng=default_rng,
    randint=lambda *a, **k: DummyArray([]),
)
numpy_stub.linalg = types.SimpleNamespace(norm=lambda _x: 1)
numpy_stub.ndarray = DummyArray
numpy_stub.uint8 = object
sys.modules["numpy"] = numpy_stub

if "PIL" not in sys.modules:
    pil_mod = types.ModuleType("PIL")
    sys.modules["PIL"] = pil_mod
    image_mod = types.ModuleType("PIL.Image")
    image_mod.Image = object
    sys.modules["PIL.Image"] = image_mod

from mock_ai.models.standard_embedding import StandardEmbeddingModel
from mock_ai.schemas.embedding_request import EmbeddingRequest


def test_standard_embedding_single_text():
    model = StandardEmbeddingModel("test-key", dimensions=5)
    req = EmbeddingRequest(input="hello", model="test")
    resp = model.get_response(req)
    assert len(resp.data) == 1
    assert resp.data[0].index == 0
    assert resp.model == "standard-embedding"
    assert resp.usage.prompt_tokens == len(str(req.input)) // 4
    assert resp.usage.completion_tokens == 0
    assert resp.data[0].embedding == [0, 1, 2, 3, 4]


def test_standard_embedding_list_and_dimensions_override():
    model = StandardEmbeddingModel("test-key", dimensions=4)
    req = EmbeddingRequest(input=["a", "b", "c"], model="test", dimensions=3)
    resp = model.get_response(req)
    assert len(resp.data) == 3
    for i, obj in enumerate(resp.data):
        assert obj.index == i
        assert obj.embedding == [0, 1, 2]
    assert resp.usage.prompt_tokens == len(str(req.input)) // 4
    assert resp.usage.completion_tokens == 0

