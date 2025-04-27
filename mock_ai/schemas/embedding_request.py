from typing import Literal

from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str
    enconding_format: Literal["float", "base64"] = "float"
    dimentions: int | None = None
    user: str | None = None
