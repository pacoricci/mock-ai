import abc

from mock_ai.schemas.embedding_out import EmbeddingResponse
from mock_ai.schemas.embedding_request import EmbeddingRequest

from . import BaseModel


class EmbeddingModel(BaseModel):
    @abc.abstractmethod
    def get_response(
        self,
        embedding_request: EmbeddingRequest,
    ) -> EmbeddingResponse:
        """Get the embedding response."""
        ...
