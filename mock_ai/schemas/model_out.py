from typing import Literal

from pydantic import BaseModel


class ModelOut(BaseModel):
    id: str
    object: Literal["model"] = "model"
    created: int
    owned_by: str


class ModelListOut(BaseModel):
    object: Literal["list"] = "list"
    data: list[ModelOut]
