from .markdown_chat import MarkdownChatModel
from .model_registry import ModelRegistry
from .parrot_chat import ParrotChatModel
from .standard_chat import StandardChatModel
from .standard_embedding import StandardEmbeddingModel
from .standard_image import StandardImageModel
from .standard_speech import StandardSpeechModel
from .structured_chat import StructuredChatModel

STANDARD_REGISTRY = ModelRegistry()

STANDARD_REGISTRY.register(StandardChatModel("mock-chat-model"))
STANDARD_REGISTRY.register(StandardEmbeddingModel("mock-embedding-model"))
STANDARD_REGISTRY.register(StandardImageModel("mock-image-model"))
STANDARD_REGISTRY.register(
    StandardImageModel("slow-mock-image-model", response_deley=10)
)
STANDARD_REGISTRY.register(StandardSpeechModel("mock-speech-model"))
STANDARD_REGISTRY.register(MarkdownChatModel())
STANDARD_REGISTRY.register(ParrotChatModel())
STANDARD_REGISTRY.register(StructuredChatModel())
