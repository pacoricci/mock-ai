import io

import numpy as np
import soundfile as sf

from mock_ai.schemas.models_response import ModelInfo
from mock_ai.schemas.speech_request import SpeechRequest

from .speech_model import SpeechModel


class StandardSpeechModel(SpeechModel):
    def __init__(
        self, key: str, sample_rate: int = 24000, amplitude: float = 0.5
    ):
        self._key = key
        self.sample_rate = sample_rate
        self.amplitude = amplitude

    @property
    def key(self) -> str:
        return self._key

    async def get_response(self, data: SpeechRequest) -> bytes:
        duration = 10
        t = np.linspace(0, duration, self.sample_rate * duration, False)
        sine = (self.amplitude * np.sin(2 * np.pi * 200 * t)).astype(np.float32)

        buffer = io.BytesIO()
        sf.write(
            buffer,
            sine,
            self.sample_rate,
            format=data.response_format.upper(),
        )
        return buffer.getvalue()

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
