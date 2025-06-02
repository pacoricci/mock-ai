from mock_ai.models.standard_embedding import StandardEmbeddingModel
from mock_ai.schemas.embedding_request import EmbeddingRequest


def test_standard_embedding_single_text():
    model = StandardEmbeddingModel("test-key", dimensions=5)
    req = EmbeddingRequest(input="hello", model="test")
    resp = model.get_response(req)
    assert len(resp.data) == 1
    assert resp.data[0].index == 0
    assert resp.model == "standard-embedding"
    assert len(resp.data[0].embedding) == 5


def test_standard_embedding_list_and_dimensions_override():
    model = StandardEmbeddingModel("test-key", dimensions=10)
    req = EmbeddingRequest(input=["a", "b", "c"], model="test", dimensions=5)
    resp = model.get_response(req)
    assert len(resp.data) == 3
    for i, obj in enumerate(resp.data):
        assert obj.index == i
        assert len(obj.embedding) == 5
