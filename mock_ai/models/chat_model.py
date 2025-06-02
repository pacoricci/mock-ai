import abc
from collections.abc import Iterator
from typing import Literal, overload

from mock_ai.schemas import ModelSettings
from mock_ai.schemas.completion_response import (
    ChatCompletionResponse,
    DeltaChoice,
    MessageChoice,
)

from .base_ai_model import BaseAIModel


class ChatModel(BaseAIModel):
    """Base interface for calling a language model."""

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[False],
    ) -> ChatCompletionResponse[MessageChoice]:
        """Get the full chat completion response."""

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[True],
    ) -> Iterator[ChatCompletionResponse[DeltaChoice]]:
        """Stream chat completion deltas."""

    @abc.abstractmethod
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: bool,
    ) -> ChatCompletionResponse | Iterator[ChatCompletionResponse[DeltaChoice]]:
        """Fetch chat completions, optionally streaming."""
