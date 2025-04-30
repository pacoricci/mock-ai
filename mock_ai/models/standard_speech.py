import io

import numpy as np
from pydub import AudioSegment

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

    def get_response(self, data: SpeechRequest) -> bytes:
        duration = 10
        t = np.linspace(0, duration, self.sample_rate * duration, False)
        sine = (self.amplitude * np.sin(2 * np.pi * 200 * t)).astype(np.float32)
        samples = (sine * 32767).astype(np.int16)

        audio_segment = AudioSegment(
            samples.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=2,
            channels=1,
        )

        mp3_buffer = io.BytesIO()
        audio_segment.export(mp3_buffer, format=data.response_format)
        return mp3_buffer.getvalue()

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
