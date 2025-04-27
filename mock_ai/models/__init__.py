import abc
from typing import final

from mock_ai.schemas.model_out import ModelOut


class HasKey(abc.ABC):
    """Mixin for classes that expose a unique model key."""

    @property
    @abc.abstractmethod
    def key(self) -> str:
        """Unique identifier for the model."""
        ...


class BaseModel(HasKey):
    @abc.abstractmethod
    def _get_model_info(self) -> ModelOut:
        """Fetch raw model metadata."""
        ...

    @final
    @property
    def model_info(self) -> ModelOut:
        """Return model info with assigned model key."""
        model_info = self._get_model_info()
        model_info.id = self.key
        return model_info
