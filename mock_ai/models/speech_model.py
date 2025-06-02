import abc

from mock_ai.schemas.speech_request import SpeechRequest

from .base_ai_model import BaseAIModel


class SpeechModel(BaseAIModel):
    @abc.abstractmethod
    def get_response(
        self,
        data: SpeechRequest,
    ) -> bytes: ...
