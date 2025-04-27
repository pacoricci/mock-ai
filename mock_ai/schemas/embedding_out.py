from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class EmbeddingObject(BaseModel):
    object: Literal["embedding"] = "embedding"
    embedding: list[float]
    index: int


class Usage(BaseModel):
    prompt_tokens: int = Field(..., ge=0)
    total_tokens: int | None = Field(None, ge=0)

    @model_validator(mode="before")
    def compute_total_tokens(
        cls: type["Usage"], values: dict[str, Any]
    ) -> dict[str, Any]:
        prompt = values.get("prompt_tokens")
        if values.get("total_tokens") is None and prompt is not None:
            values["total_tokens"] = prompt
        return values


class EmbeddingResponse(BaseModel):
    object: Literal["list"] = "list"
    data: list[EmbeddingObject]
    model: str
    usage: Usage
