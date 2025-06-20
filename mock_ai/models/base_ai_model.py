import abc
from typing import final

from mock_ai.schemas.models_response import ModelInfo


class HasKey(abc.ABC):
    """Mixin for classes that expose a unique model key."""

    @property
    @abc.abstractmethod
    def key(self) -> str:
        """Unique identifier for the model."""
        ...


class BaseAIModel(HasKey):
    @abc.abstractmethod
    def _get_model_info(self) -> ModelInfo:
        """Fetch raw model metadata."""
        ...

    @final
    @property
    def model_info(self) -> ModelInfo:
        """Return model info with assigned model key."""
        model_info = self._get_model_info()
        model_info.id = self.key
        return model_info
