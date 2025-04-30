from typing import Generic, TypeVar

from pydantic import BaseModel

from .usage import Usage


class ImageUrl(BaseModel):
    url: str


class ImageB64(BaseModel):
    b64_json: str


T = TypeVar("T", ImageUrl, ImageB64)


class ImageResponse(BaseModel, Generic[T]):
    created: int
    data: list[T]
    usage: Usage | None = None
