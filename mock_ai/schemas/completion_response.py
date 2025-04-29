from typing import Literal

from pydantic import BaseModel

from .usage import Usage


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
