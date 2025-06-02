from typing import Literal

from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str
    encoding_format: Literal["float", "base64"] = "float"
    dimensions: int | None = None
    user: str | None = None
