from typing import Literal

from pydantic import BaseModel


class SpeechRequest(BaseModel):
    input: str
    model: str
    voice: str
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"
    speed: float = 1.0
