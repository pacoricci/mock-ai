from .model_registry import ModelRegistry
from .standard_chat import StandardChatModel
from .standard_embedding import StandardEmbeddingModel


class StandardRegistry(ModelRegistry): ...


STANDARD_REGISTRY = StandardRegistry()
STANDARD_REGISTRY.register(StandardChatModel("standard-chat-model"))
STANDARD_REGISTRY.register(StandardEmbeddingModel("standard-embedding-model"))
