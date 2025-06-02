from typing import Literal

from mock_ai.schemas.image_request import ImageRequest
from mock_ai.schemas.image_response import (
    ImageB64,
    ImageResponse,
    ImageUrl,
)
from mock_ai.schemas.models_response import ModelInfo
from mock_ai.utils import (
    gen_image_id,
    generate_noise_image_from_string,
    img_to_b64,
    parse_dimensions,
)

from .image_model import ImageModel


class StandardImageModel(ImageModel):
    """Standard image model."""

    def __init__(self, key: str):
        self._key = key

    @property
    def key(self) -> str:
        return self._key

    def get_response(
        self, data: ImageRequest, response_format: Literal["url", "b64_json"]
    ) -> ImageResponse:
        if response_format == "url":
            image_urls = []
            for _ in range(data.n):
                image_id = gen_image_id(f"{data.size}|{data.output_format}")
                image_urls.append(
                    ImageUrl(
                        url=f"private/images/{image_id}.{data.output_format.lower()}"
                    )
                )
            return ImageResponse(
                created=0,
                data=image_urls,
            )
        elif response_format == "b64_json":
            width, height = parse_dimensions(data.size)
            b64_images = []
            for i in range(data.n):
                img = generate_noise_image_from_string(
                    f"{data.prompt}{i}", width, height
                )
                b64 = img_to_b64(img, format=data.output_format)
                b64_images.append(ImageB64(b64_json=b64))
            return ImageResponse(
                created=0,
                data=b64_images,
            )
        raise ValueError("Invalid response format.")

    def _get_model_info(self) -> ModelInfo:
        """Fetch raw model metadata."""
        return ModelInfo(id="", created=0, owned_by="")
