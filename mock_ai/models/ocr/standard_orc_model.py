from __future__ import annotations

import asyncio

from mock_ai.schemas.models_response import ModelInfo
from mock_ai.schemas.ocr_request import OcrRequest
from mock_ai.schemas.ocr_response import (
    Dimensions,
    Document,
    ImageRegion,
    Page,
)
from mock_ai.utils import generate_noise_image_from_string, img_to_b64

from .ocr_model import OcrModel


class StandardOcrModel(OcrModel):
    """Standard OCR model returning a mock parsed document.

    Generates a single-page document with simple markdown text extracted from
    the input URL. Optionally embeds a small base64 image region when
    `include_image_base64` is True.
    """

    def __init__(self, key: str, response_delay: float | None = None):
        self._key = key
        self.response_delay = response_delay

    @property
    def key(self) -> str:
        return self._key

    async def get_response(self, embedding_request: OcrRequest) -> Document:
        if self.response_delay:
            await asyncio.sleep(self.response_delay)

        url = embedding_request.document.document_url

        markdown = (
            f"# OCR Result\n\n"
            f"Source: {url}\n\n"
            "This is a mock OCR extraction produced by StandardOcrModel.\n"
            "Content is deterministic placeholder text."
        )

        markdown_2 = (
            f"# Second Page\n\n"
            f"Source: {url}\n\n"
            "This is a mock OCR extraction produced by StandardOcrModel.\n"
            "This is the second page"
        )
        images: list[ImageRegion] = []
        if embedding_request.include_image_base64:
            # Produce a tiny deterministic image preview tied to the URL
            width, height = 100, 60
            img = generate_noise_image_from_string(url, width, height)
            b64 = img_to_b64(img, format="PNG")
            images.append(
                ImageRegion(
                    id="img-0",
                    top_left_x=0,
                    top_left_y=0,
                    bottom_right_x=width,
                    bottom_right_y=height,
                    image_base64=b64,
                )
            )

        page = Page(
            index=0,
            markdown=markdown,
            dimensions=Dimensions(dpi=0, width=0, height=0),
            images=images,
        )

        page_2 = Page(
            index=1,
            markdown=markdown_2,
            dimensions=Dimensions(dpi=0, width=0, height=0),
            images=[],
        )

        return Document(pages=[page, page_2])

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
