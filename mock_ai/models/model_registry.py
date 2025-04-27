from collections.abc import Iterator
from typing import Generic, TypeVar

from mock_ai.schemas.model_out import ModelListOut

from . import BaseModel, HasKey

T = TypeVar("T", bound="HasKey")


class Registry(Generic[T]):
    def __init__(self) -> None:
        self._store: dict[str, T] = {}

    def register(self, obj: T) -> T:
        self._store[obj.key] = obj
        return obj

    def get(self, key: str) -> T | None:
        return self._store.get(key)

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def __iter__(self) -> Iterator[T]:
        return iter(self._store.values())

    def __len__(self) -> int:
        return len(self._store)


class ModelRegistry(Registry[BaseModel]):
    def get_models(self) -> ModelListOut:
        return ModelListOut(
            data=[model.model_info for model in self._store.values()]
        )
