import base64
import hashlib
import io
import random
import re
import string
import time
import uuid
from collections.abc import Iterator

import numpy as np
from PIL import Image
from pydantic import BaseModel

from mock_ai.schemas.completion_response import (
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
    allowed_chars = string.ascii_letters + string.digits + " " * 10
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


def generate_noise_image_from_string(
    key: str,
    width: int,
    height: int,
    loc: float = 0.0,
    scale: float = 1.0,
) -> Image.Image:
    h = hashlib.md5(key.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big", signed=False)
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=loc, scale=scale, size=(height, width, 3))

    noise_min = noise.min()
    noise_max = noise.max()
    noise_normalized = (noise - noise_min) / (noise_max - noise_min)
    noise_255 = (noise_normalized * 255).astype(np.uint8)

    return Image.fromarray(noise_255, mode="RGB")


def img_to_b64(img: Image.Image, format: str) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)

    img_bytes = buffer.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    return img_b64


def parse_dimensions(s: str) -> tuple[int, int]:
    pattern = re.compile(r"^(\d+)x(\d+)$")
    match = pattern.match(s)
    if not match:
        raise ValueError(
            "Invalid dimensions format. Expected format: 'WIDTHxHEIGHT'."
        )
    return int(match.group(1)), int(match.group(2))


_UUID_HEX_LEN = 32
_CHECKSUM_HEX_LEN = 32


def _md5_hexdigest(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def gen_image_id(payload: str) -> str:
    prefix = uuid.uuid4().hex
    b64 = (
        base64.urlsafe_b64encode(payload.encode("utf-8"))
        .rstrip(b"=")
        .decode("ascii")
    )
    checksum = _md5_hexdigest((prefix + b64).encode("utf-8"))
    return f"{prefix}{b64}{checksum}"


def check_image_id(img_id: str) -> bool:
    if len(img_id) < (_UUID_HEX_LEN + _CHECKSUM_HEX_LEN):
        return False
    body = img_id[:-_CHECKSUM_HEX_LEN]
    provided_chk = img_id[-_CHECKSUM_HEX_LEN:]
    expected_chk = _md5_hexdigest(body.encode("utf-8"))
    return provided_chk == expected_chk


def get_data_from_image_id(img_id: str) -> str | None:
    if not check_image_id(img_id):
        return None
    b64_part = img_id[_UUID_HEX_LEN:-_CHECKSUM_HEX_LEN]
    padding = "=" * (-len(b64_part) % 4)
    try:
        return base64.urlsafe_b64decode(b64_part + padding).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
