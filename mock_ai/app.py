from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response, StreamingResponse

from mock_ai.models.chat_model import ChatModel
from mock_ai.models.embedding_model import EmbeddingModel
from mock_ai.models.standard_registry import STANDARD_REGISTRY
from mock_ai.schemas.chat_completion_request import (
    ChatCompletionRequest,
)
from mock_ai.schemas.embedding_out import EmbeddingResponse
from mock_ai.schemas.embedding_request import EmbeddingRequest
from mock_ai.schemas.model_out import ModelInfo, ModelsResponse
from mock_ai.utils import SSEEncoder

app = FastAPI()


@app.get("/v1/models/", response_model=ModelsResponse)
async def models() -> ModelsResponse:
    return STANDARD_REGISTRY.get_models()


@app.get("/v1/models/{model_name}")
async def model(model_name: str) -> ModelInfo:
    model = STANDARD_REGISTRY.get(model_name)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    return model.model_info


@app.post("/v1/chat/completions")
async def chat_completions(
    data: ChatCompletionRequest,
) -> Response:
    model = STANDARD_REGISTRY.get(data.model)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    if not isinstance(model, ChatModel):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Model `{data.model}` is not a chat model",
        )
    model_settings = data.to_settings()
    if data.stream:
        stream_response = model.get_response(model_settings, True)
        return StreamingResponse(
            SSEEncoder(stream_response), media_type="text/event-stream"
        )
    else:
        model_response = model.get_response(model_settings, False)
        return Response(
            content=model_response.model_dump_json(),
            media_type="application/json",
        )


@app.post("/v1/embeddings")
async def embeddings(
    data: EmbeddingRequest,
) -> EmbeddingResponse:
    model = STANDARD_REGISTRY.get(data.model)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    if not isinstance(model, EmbeddingModel):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Model `{data.model}` is not an embedding model",
        )
    model_response = model.get_response(data)
    return model_response
