from .chat.markdown_chat import MarkdownChatModel
from .chat.parrot_chat import ParrotChatModel
from .chat.standard_chat import StandardChatModel
from .chat.structured_chat import StructuredChatModel
from .embedding.standard_embedding import StandardEmbeddingModel
from .model_registry import ModelRegistry
from .ocr.standard_orc_model import StandardOcrModel
from .speech.standard_speech import StandardSpeechModel
from .text_to_image.standard_image import StandardImageModel

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
STANDARD_REGISTRY.register(StandardOcrModel("mock-ocr"))
