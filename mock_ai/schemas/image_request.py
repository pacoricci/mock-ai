from typing import Literal

from pydantic import BaseModel


class ImageRequest(BaseModel):
    prompt: str
    model: str
    n: int = 1
    size: str = "1024x1024"
    output_format: Literal["png", "jpeg"] = "png"
    response_format: Literal["url", "b64_json"] = "url"
