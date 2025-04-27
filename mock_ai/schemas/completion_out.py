from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class PromptTokensDetails(BaseModel):
    cached_tokens: int
    audio_tokens: int


class CompletionTokensDetails(BaseModel):
    reasoning_tokens: int
    audio_tokens: int
    accepted_prediction_tokens: int
    rejected_prediction_tokens: int


class Usage(BaseModel):
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int | None = Field(None, ge=0)
    prompt_tokens_details: PromptTokensDetails | None = None
    completion_tokens_details: CompletionTokensDetails | None = None

    @model_validator(mode="before")
    def compute_total_tokens(
        cls: type["Usage"], values: dict[str, Any]
    ) -> dict[str, Any]:
        prompt = values.get("prompt_tokens")
        completion = values.get("completion_tokens")
        if (
            values.get("total_tokens") is None
            and prompt is not None
            and completion is not None
        ):
            values["total_tokens"] = prompt + completion
        return values


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "developer"]
    content: str
    refusal: str | None = None


class MessageChoice(BaseModel):
    index: int
    message: Message
    logprobs: dict | None = None
    finish_reason: str | None = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[MessageChoice]
    usage: Usage
    system_fingerprint: str


class Delta(BaseModel):
    content: str | None = None


class DeltaChoice(BaseModel):
    index: int
    delta: Delta
    logprobs: dict | None = None
    finish_reason: str | None = None


class ChatCompletionDelta(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[DeltaChoice]
    usage: Usage | None = None
    system_fingerprint: str
