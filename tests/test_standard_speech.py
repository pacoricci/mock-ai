import io
import wave

import pytest
import soundfile as sf

from mock_ai.models.standard_speech import StandardSpeechModel
from mock_ai.schemas.speech_request import SpeechRequest


def test_standard_speech_model():
    model = StandardSpeechModel(key="tts-1")
    request = SpeechRequest(
        model="tts-1", input="test", voice="alloy", response_format="wav"
    )
    result = model.get_response(request)

    assert isinstance(result, bytes)
    assert len(result) > 0

    with io.BytesIO(result) as buffer:
        with wave.open(buffer, "rb") as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == 24000


def test_standard_speech_model_flac():
    model = StandardSpeechModel(key="tts-1")
    request = SpeechRequest(
        model="tts-1", input="test", voice="alloy", response_format="flac"
    )
    result = model.get_response(request)

    assert isinstance(result, bytes)
    assert len(result) > 0

    with io.BytesIO(result) as buffer:
        with sf.SoundFile(buffer, "r") as sound_file:
            assert sound_file.channels == 1
            assert sound_file.samplerate == 24000
            assert sound_file.format == "FLAC"
