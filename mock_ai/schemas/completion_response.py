import time
import uuid
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from .usage import Usage


def id_factory() -> str:
    return f"chatcmpl-{uuid.uuid4()}"


def created_factory() -> int:
    return int(time.time())


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "developer"] = "assistant"
    content: str
    refusal: str | None = None


class Delta(BaseModel):
    content: str | None = None


class Choice(BaseModel):
    index: int = 0
    logprobs: dict | None = None
    finish_reason: str | None = None


class MessageChoice(Choice):
    message: Message


class DeltaChoice(Choice):
    delta: Delta


T = TypeVar("T", DeltaChoice, MessageChoice)


class ChatCompletionResponse(BaseModel, Generic[T]):
    id: str = Field(default_factory=id_factory)
    object: Literal["chat.completion", "chat.completion.chunk"] = (
        "chat.completion"
    )
    created: int = Field(default_factory=created_factory)
    model: str
    choices: list[T]
    usage: Usage | None = None
    system_fingerprint: str = "fp_abc123"
