from mock_ai.schemas.embedding_request import EmbeddingRequest
from mock_ai.schemas.embedding_response import (
    EmbeddingObject,
    EmbeddingResponse,
    Usage,
)
from mock_ai.schemas.models_response import ModelInfo
from mock_ai.utils import normal_from_string

from .embedding_model import EmbeddingModel


class StandardEmbeddingModel(EmbeddingModel):
    """Standard embedding model."""

    def __init__(self, key: str, dimensions: int = 1536):
        self._key = key
        self.dimensions = dimensions

    @property
    def key(self) -> str:
        return self._key

    def get_response(self, data: EmbeddingRequest) -> EmbeddingResponse:
        m = data.dimensions if data.dimensions else self.dimensions
        batch = data.input if isinstance(data.input, list) else [data.input]
        embedding_object_list = [
            EmbeddingObject(
                index=i, embedding=normal_from_string(s, m).tolist()
            )
            for i, s in enumerate(batch)
        ]

        return EmbeddingResponse(
            data=embedding_object_list,
            model="standard-embedding",
            usage=Usage(
                prompt_tokens=len(str(data.input)) // 4, completion_tokens=0
            ),
        )

    def _get_model_info(self) -> ModelInfo:
        """Fetch raw model metadata."""
        return ModelInfo(id="", created=0, owned_by="")
