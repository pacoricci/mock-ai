import abc
from typing import Literal, overload

from mock_ai.schemas.ocr_request import OcrRequest
from mock_ai.schemas.ocr_response import Document

from .base_ai_model import BaseAIModel


class OcrModel(BaseAIModel):
    @abc.abstractmethod
    async def get_response(
        self,
        embedding_request: OcrRequest,
    ) -> Document: ...
