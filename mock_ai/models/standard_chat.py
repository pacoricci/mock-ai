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
from mock_ai.utils import TokenBatchFactory

from .chat_model import ChatModel


class StandardChatModel(ChatModel):
    COMPLETIONS_TOKENS_LIMIT = 1000
    BATCH_PER_SECOND = 10
    TOKEN_PER_BATCH = 10

    def __init__(
        self,
        key: str,
        completions_tokens_limit: int = COMPLETIONS_TOKENS_LIMIT,
        batch_per_second: int = BATCH_PER_SECOND,
        token_per_batch: int = TOKEN_PER_BATCH,
    ):
        self._key = key
        self.batch_per_second = batch_per_second
        self.completions_tokens_limit = completions_tokens_limit
        self.token_per_batch = token_per_batch

    @property
    def key(self) -> str:
        return self._key

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
        MAX_COMPLITION_TOKENS = self.completions_tokens_limit

        if stream:

            def stream_response() -> Generator[
                ChatCompletionResponse[DeltaChoice], Any, None
            ]:
                tokens_bank = MAX_COMPLITION_TOKENS
                while tokens_bank > 0:
                    batch_size = min(self.TOKEN_PER_BATCH, tokens_bank)
                    tokens_bank -= batch_size

                    time.sleep(1 / self.batch_per_second)

                    yield ChatCompletionResponse(
                        model=self.key,
                        choices=[
                            DeltaChoice(
                                delta=Delta(
                                    content=next(TokenBatchFactory(batch_size))
                                ),
                            )
                        ],
                    )
                if model_settings.needs_usage():
                    prompt_tokens = len(str(model_settings.messages)) // 4
                    yield ChatCompletionResponse(
                        model=self.key,
                        choices=[],
                        usage=Usage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=4,
                        ),
                    )

            return stream_response()
        else:
            return ChatCompletionResponse(
                model=self.key,
                choices=[
                    MessageChoice(
                        index=0,
                        message=Message(
                            role="assistant",
                            content=next(
                                TokenBatchFactory(MAX_COMPLITION_TOKENS)
                            ),
                        ),
                    )
                ],
                usage=Usage(prompt_tokens=1, completion_tokens=1),
            )

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
