import abc
from collections.abc import Iterator
from typing import Literal, overload

from mock_ai.schemas import ModelSettings
from mock_ai.schemas.completion_out import (
    ChatCompletionDelta,
    ChatCompletionResponse,
)

from . import BaseModel


class ChatModel(BaseModel):
    """Base interface for calling a language model."""

    @overload
    @abc.abstractmethod
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[False],
    ) -> ChatCompletionResponse:
        """Get the full chat completion response."""

    @overload
    @abc.abstractmethod
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[True],
    ) -> Iterator[ChatCompletionDelta]:
        """Stream chat completion deltas."""

    @abc.abstractmethod
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: bool,
    ) -> ChatCompletionResponse | Iterator[ChatCompletionDelta]:
        """Fetch chat completions, optionally streaming."""
