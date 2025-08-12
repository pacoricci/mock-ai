import base64
import hashlib
import io
import random
import re
import string
import uuid
from collections.abc import AsyncIterator

import numpy as np
from PIL import Image
from pydantic import BaseModel


class SSEEncoder:
    def __init__(
        self,
        iterator: AsyncIterator[BaseModel]
        | AsyncIterator[dict]
        | AsyncIterator[str],
    ) -> None:
        self.iterator = iterator

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        item = await anext(self.iterator)
        if isinstance(item, str):
            return f"data: {item}\n\n".encode()
        if isinstance(item, dict):
            return f"data: {item}\n\n".encode()
        if isinstance(item, BaseModel):
            return f"data: {item.model_dump_json()}\n\n".encode()
        raise TypeError("Unsupported item type")


def generate_random_string(length: int) -> str:
    allowed_chars = string.ascii_letters + string.digits + " " * 10
    return "".join(random.choices(allowed_chars, k=length))


def random_gen_from_string(key: str) -> np.random.Generator:
    h = hashlib.md5(key.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big", signed=False)
    return np.random.default_rng(seed)


def normal_from_string(
    key: str, n: int, loc: float = 0.0, scale: float = 1.0
) -> np.ndarray:
    rng = random_gen_from_string(key)
    v = rng.normal(loc=loc, scale=scale, size=n)
    normalized_v = v / np.linalg.norm(v)
    return normalized_v


def generate_noise_image_from_string(
    key: str,
    width: int,
    height: int,
    loc: float = 0.0,
    scale: float = 1.0,
) -> Image.Image:
    rng = random_gen_from_string(key)
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


class Token:
    def __init__(self, n: int = 1024):
        self.n = n

    def __getitem__(self, key: int) -> str:
        if key > self.n - 1 or key < 0:
            raise IndexError("Index out of range")
        suffix = "\n" if key % 100 == 0 else (" " if key % 10 == 0 else "")
        return f"[{key}]{suffix}"

    def __len__(self) -> int:
        return self.n


class TokenBatchFactory:
    def __init__(self, batch_size: int = 1, n: int = 1024, stop_token: int = 0):
        self.token = Token(n)
        self.batch_size = batch_size
        self.n = n
        self.stop_token = stop_token
        self.end = False

    def __iter__(self) -> "TokenBatchFactory":
        return self

    def __next__(self) -> str:
        if self.end:
            raise StopIteration
        indexes = np.random.randint(0, self.n, self.batch_size).tolist()
        tokens = []
        for index in indexes:
            if index == self.stop_token:
                break
            tokens.append(self.token[index])
        return "".join(tokens)

    def __len__(self) -> int:
        return self.batch_size

    def __mul__(self, other: int) -> "TokenBatchFactory":
        if isinstance(other, int):
            self.batch_size *= other
            return self
        raise TypeError("Multiplication is only supported with integers.")

    def __rmul__(self, other: int) -> "TokenBatchFactory":
        return self.__mul__(other)
