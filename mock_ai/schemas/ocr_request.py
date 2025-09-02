from typing import Literal

from pydantic import BaseModel


class Document(BaseModel):
    type: Literal["document_url"] = "document_url"
    document_url: str


class OcrRequest(BaseModel):
    model: str
    document: Document
    include_image_base64: bool = False
