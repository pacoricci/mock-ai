import json
import random
import string
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


def _random_string(length: int = 8) -> str:
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def _from_schema(schema: dict) -> Any:
    type_ = schema.get("type")
    if type_ == "object":
        return {
            key: _from_schema(sub)
            for key, sub in schema.get("properties", {}).items()
        }
    if type_ == "array":
        return [_from_schema(schema.get("items", {}))]
    if type_ == "integer":
        return random.randint(0, 100)
    if type_ == "number":
        return random.random() * 100
    if type_ == "boolean":
        return random.choice([True, False])
    return _random_string()


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
        max_completion_tokens = int(
            min(
                self.completions_tokens_limit,
                model_settings.tokens_upper_limit,
            )
        )

        fmt = model_settings.response_format or {}
        if fmt:
            if fmt.get("type") == "json_schema":
                payload = _from_schema(fmt.get("json_schema", {}))
            else:
                payload = {"mock": _random_string(4)}
            content = json.dumps(payload)

            if stream:

                def stream_response() -> Generator[
                    ChatCompletionResponse[DeltaChoice], Any, None
                ]:
                    for i in range(0, len(content), 10):
                        time.sleep(1 / self.batch_per_second)
                        yield ChatCompletionResponse(
                            model=self.key,
                            choices=[
                                DeltaChoice(
                                    delta=Delta(content=content[i : i + 10])
                                )
                            ],
                        )
                    if model_settings.needs_usage():
                        prompt_tokens = len(str(model_settings.messages)) // 4
                        completion_tokens = len(content) // 4
                        yield ChatCompletionResponse(
                            model=self.key,
                            choices=[],
                            usage=Usage(
                                prompt_tokens=prompt_tokens,
                                completion_tokens=completion_tokens,
                            ),
                        )

                return stream_response()

            return ChatCompletionResponse(
                model=self.key,
                choices=[
                    MessageChoice(
                        index=0,
                        message=Message(role="assistant", content=content),
                    )
                ],
                usage=Usage(
                    prompt_tokens=len(str(model_settings.messages)) // 4,
                    completion_tokens=len(content) // 4,
                ),
            )

        if stream:

            def stream_response() -> Generator[
                ChatCompletionResponse[DeltaChoice], Any, None
            ]:
                tokens_bank = max_completion_tokens
                while tokens_bank > 0:
                    batch_size = min(self.token_per_batch, tokens_bank)
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
                                TokenBatchFactory(max_completion_tokens)
                            ),
                        ),
                    )
                ],
                usage=Usage(prompt_tokens=1, completion_tokens=1),
            )

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
