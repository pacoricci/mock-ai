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


class ChatCompletionRequest(ModelSettings):
    model: str
    stream: bool = False

    def to_settings(self) -> ModelSettings:
        data = self.model_dump(exclude={"model", "stream"}, exclude_unset=True)
        return ModelSettings(**data)
