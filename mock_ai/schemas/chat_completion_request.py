from pydantic import BaseModel


class ModelSettings(BaseModel):
    messages: list[dict]
    max_completion_tokens: int | None = None
    max_tokens: int | None = None
    temperature: float | None = 1
    stream_options: dict | None = None

    def needs_usage(self) -> bool:
        return (
            isinstance(self.stream_options, dict)
            and "include_usage" in self.stream_options
        )

    @property
    def tokens_upper_limit(self) -> int | float:
        upper_limit = float("inf")
        if self.max_tokens:
            upper_limit = self.max_tokens
        if self.max_completion_tokens:
            upper_limit = min(upper_limit, self.max_completion_tokens)
        return upper_limit


class ChatCompletionRequest(ModelSettings):
    model: str
    stream: bool = False

    def to_settings(self) -> ModelSettings:
        data = self.model_dump(exclude={"model", "stream"}, exclude_unset=True)
        return ModelSettings(**data)
