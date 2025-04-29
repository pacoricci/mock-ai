import abc

from mock_ai.schemas.embedding_request import EmbeddingRequest
from mock_ai.schemas.embedding_response import EmbeddingResponse

from .base_ai_model import BaseAIModel


class EmbeddingModel(BaseAIModel):
    @abc.abstractmethod
    def get_response(
        self,
        embedding_request: EmbeddingRequest,
    ) -> EmbeddingResponse:
        """Get the embedding response."""
        ...
