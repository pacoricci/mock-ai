import hashlib
import random
import string
import time
from collections.abc import Iterator

import numpy as np
from pydantic import BaseModel

from mock_ai.schemas.completion_out import (
    ChatCompletionDelta,
    ChatCompletionResponse,
    Delta,
    DeltaChoice,
    Message,
    MessageChoice,
    Usage,
)


class SSEEncoder:
    def __init__(self, iterator: Iterator[BaseModel]) -> None:
        self.iterator = iterator

    def __iter__(self):
        return self

    def __next__(self) -> bytes:
        item = next(self.iterator)
        return f"data: {item.model_dump_json()}\n\n".encode()


def generate_random_string(length: int) -> str:
    allowed_chars = string.ascii_letters + string.digits
    return "".join(random.choices(allowed_chars, k=length))


def generate_chat_completions_object(
    model: str,
    content: str,
    prompt_tokens: int,
    completion_tokens: int,
    finsih_reason: str | None = "stop",
) -> ChatCompletionResponse:
    return ChatCompletionResponse(
        id="chatcmpl-123",
        object="chat.completion",
        created=int(time.time()),
        model=model,
        system_fingerprint="fp_44709d6fcb",
        choices=[
            MessageChoice(
                index=1,
                message=Message(role="assistant", content=content),
                finish_reason=finsih_reason,
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        ),
    )


def generate_chat_completion_chunk(
    model: str,
    chunk_output_message: str,
    usage: Usage | None = None,
    finish_reason: str | None = None,
) -> ChatCompletionDelta:
    result = ChatCompletionDelta(
        id="chatcmpl-123",
        created=int(time.time()),
        model=model,
        system_fingerprint="fp_44709d6fcb",
        choices=[
            DeltaChoice(
                index=1,
                delta=Delta(content=chunk_output_message),
                finish_reason=finish_reason,
            )
        ],
    )
    if usage:
        result.usage = usage
    return result


def normal_from_string(
    key: str, n: int, loc: float = 0.0, scale: float = 1.0
) -> np.ndarray:
    h = hashlib.md5(key.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big", signed=False)
    rng = np.random.default_rng(seed)
    return rng.normal(loc=loc, scale=scale, size=n)
