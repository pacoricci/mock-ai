import time
from collections.abc import Generator, Iterator
from typing import Any, Literal, overload

from mock_ai.schemas.chat_completion_request import ModelSettings
from mock_ai.schemas.completion_response import (
    ChatCompletionResponse,
    Delta,
    DeltaChoice,
    Message,
    MessageChoice,
    Usage,
)
from mock_ai.schemas.models_response import ModelInfo

from .chat_model import ChatModel


class ParrotChatModel(ChatModel):
    """Chat model that echoes the last user message."""

    @property
    def key(self) -> str:
        return "parrot-chat-model"

    def _last_user_message(self, settings: ModelSettings) -> str:
        for msg in reversed(settings.messages):
            if msg.get("role") == "user":
                return str(msg.get("content", ""))
        return ""

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[False],
    ) -> ChatCompletionResponse[MessageChoice]: ...

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[True],
    ) -> Iterator[ChatCompletionResponse[DeltaChoice]]: ...

    def get_response(
        self,
        model_settings: ModelSettings,
        stream: bool,
    ) -> ChatCompletionResponse | Iterator[ChatCompletionResponse[DeltaChoice]]:
        message = self._last_user_message(model_settings)
        if stream:

            def stream_response() -> Generator[
                ChatCompletionResponse[DeltaChoice], Any, None
            ]:
                for i in range(0, len(message), 10):
                    time.sleep(0.01)
                    yield ChatCompletionResponse(
                        model=self.key,
                        choices=[
                            DeltaChoice(
                                delta=Delta(content=message[i : i + 10])
                            )
                        ],
                    )
                if model_settings.needs_usage():
                    prompt_tokens = len(str(model_settings.messages)) // 4
                    completion_tokens = len(message) // 4
                    yield ChatCompletionResponse(
                        model=self.key,
                        choices=[],
                        usage=Usage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                        ),
                    )

            return stream_response()
        else:
            return ChatCompletionResponse(
                model=self.key,
                choices=[
                    MessageChoice(
                        index=0,
                        message=Message(role="assistant", content=message),
                    )
                ],
                usage=Usage(
                    prompt_tokens=len(str(model_settings.messages)) // 4,
                    completion_tokens=len(message) // 4,
                ),
            )

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
