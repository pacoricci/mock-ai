import time
from collections.abc import Generator, Iterator
from typing import Any, Literal, overload

from mock_ai.schemas.chat_completion_request import ModelSettings
from mock_ai.schemas.completion_response import (
    ChatCompletionDelta,
    ChatCompletionResponse,
    Usage,
)
from mock_ai.schemas.models_response import ModelInfo

from ..utils import (
    generate_chat_completion_chunk,
    generate_chat_completions_object,
    generate_random_string,
)
from .chat_model import ChatModel


class StandardChatModel(ChatModel):
    def __init__(self, key: str, max_message_lenght: int = 10_000):
        self._key = key
        self.message_lenght = max_message_lenght

    @property
    def key(self) -> str:
        return self._key

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[False],
    ) -> ChatCompletionResponse: ...

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[True],
    ) -> Iterator[ChatCompletionDelta]: ...

    def get_response(
        self,
        model_settings: ModelSettings,
        stream: bool,
    ) -> ChatCompletionResponse | Iterator[ChatCompletionDelta]:
        MAX_COMPLITION_TOKENS = (
            model_settings.max_completion_tokens
            if model_settings.max_completion_tokens
            else model_settings.max_tokens
        )
        MAX_COMPLITION_LENGTH = (
            4 * MAX_COMPLITION_TOKENS
            if MAX_COMPLITION_TOKENS
            else self.message_lenght
        )

        if stream:

            def stream_response() -> Generator[ChatCompletionDelta, Any, None]:
                for _ in range(MAX_COMPLITION_LENGTH // 10):
                    time.sleep(0.05)
                    random_string = generate_random_string(10)
                    yield generate_chat_completion_chunk(
                        model=self.key, chunk_output_message=random_string
                    )
                if (
                    model_settings.stream_options
                    and model_settings.stream_options.get("include_usage")
                ):
                    prompt_tokens = len(str(model_settings.messages))
                    usage = Usage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=MAX_COMPLITION_LENGTH // 4,
                    )
                    yield generate_chat_completion_chunk(
                        model=self.key, chunk_output_message="", usage=usage
                    )

            return stream_response()
        else:
            random_string = generate_random_string(MAX_COMPLITION_LENGTH)
            return generate_chat_completions_object(
                model=self.key,
                content=random_string,
                prompt_tokens=len(str(model_settings.messages)) // 4,
                completion_tokens=MAX_COMPLITION_LENGTH // 4,
            )

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
