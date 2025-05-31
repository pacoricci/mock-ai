import abc
from typing import Literal, overload

from mock_ai.schemas.image_request import ImageRequest
from mock_ai.schemas.image_response import ImageB64, ImageResponse, ImageUrl

from .base_ai_model import BaseAIModel


class ImageModel(BaseAIModel):
    @overload
    def get_response(
        self, embedding_request: ImageRequest, response_format: Literal["url"]
    ) -> ImageResponse[ImageUrl]: ...

    @overload
    def get_response(
        self,
        embedding_request: ImageRequest,
        response_format: Literal["b64_json"],
    ) -> ImageResponse[ImageB64]: ...

    @abc.abstractmethod
    def get_response(
        self,
        embedding_request: ImageRequest,
        response_format: Literal["url", "b64_json"],
    ) -> ImageResponse[ImageUrl] | ImageResponse[ImageB64]: ...
