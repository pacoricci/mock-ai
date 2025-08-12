import asyncio
import json
import random
import string
from collections.abc import AsyncGenerator, AsyncIterator
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


class StructuredChatModel(ChatModel):
    """Chat model that returns JSON according to ``response_format``."""

    def __init__(self, key: str = "structured-chat-model") -> None:
        self._key = key

    @property
    def key(self) -> str:  # pragma: no cover - simple accessor
        return self._key

    @overload
    async def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[False],
    ) -> ChatCompletionResponse[MessageChoice]: ...

    @overload
    async def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[True],
    ) -> AsyncIterator[ChatCompletionResponse[DeltaChoice]]: ...

    async def get_response(
        self,
        model_settings: ModelSettings,
        stream: bool,
    ) -> (
        ChatCompletionResponse
        | AsyncIterator[ChatCompletionResponse[DeltaChoice]]
    ):
        fmt = model_settings.response_format or {}
        if fmt.get("type") == "json_schema":
            payload = _from_schema(fmt.get("json_schema", {}))
        else:
            payload = {"mock": _random_string(4)}

        content = json.dumps(payload)

        if stream:

            async def stream_response() -> AsyncGenerator[
                ChatCompletionResponse[DeltaChoice]
            ]:
                for i in range(0, len(content), 10):
                    await asyncio.sleep(0.01)
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

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")
