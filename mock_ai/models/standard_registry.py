from .model_registry import ModelRegistry
from .standard_chat import StandardChatModel
from .standard_embedding import StandardEmbeddingModel
from .standard_image import StandardImageModel
from .standard_speech import StandardSpeechModel

STANDARD_REGISTRY = ModelRegistry()

STANDARD_REGISTRY.register(
    StandardChatModel("standard-chat-model", max_message_lenght=1000)
)
STANDARD_REGISTRY.register(StandardEmbeddingModel("standard-embedding-model"))
STANDARD_REGISTRY.register(StandardImageModel("standard-image-model"))
STANDARD_REGISTRY.register(StandardSpeechModel("standard-speech-model"))
