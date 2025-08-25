import io

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mock_ai.mcp_app import mcp
from mock_ai.models import ChatModel, EmbeddingModel, ImageModel, SpeechModel
from mock_ai.models.standard_registry import STANDARD_REGISTRY
from mock_ai.schemas.chat_completion_request import ChatCompletionRequest
from mock_ai.schemas.embedding_request import EmbeddingRequest
from mock_ai.schemas.embedding_response import EmbeddingResponse
from mock_ai.schemas.image_request import ImageRequest
from mock_ai.schemas.image_response import ImageB64, ImageResponse, ImageUrl
from mock_ai.schemas.models_response import ModelInfo, ModelsResponse
from mock_ai.schemas.speech_request import SpeechRequest
from mock_ai.settings import auth_settings, cors_settings
from mock_ai.utils import (
    SSEEncoder,
    generate_noise_image_from_string,
    get_data_from_image_id,
    parse_dimensions,
)

security = HTTPBearer(auto_error=False)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    if auth_settings.bearer_tokens and (
        not credentials
        or credentials.credentials not in auth_settings.bearer_tokens
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    dependencies = (
        [Depends(verify_token)] if auth_settings.bearer_tokens else []
    )
    app = FastAPI(dependencies=dependencies)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.allow_origins,
        allow_credentials=cors_settings.allow_credentials,
        allow_methods=cors_settings.allow_methods,
        allow_headers=cors_settings.allow_headers,
    )

    return app


api_app = create_app()


@api_app.get("/v1/models/", response_model=ModelsResponse)
async def models() -> ModelsResponse:
    return STANDARD_REGISTRY.get_models()


@api_app.get("/v1/models/{model_name}")
async def model(model_name: str) -> ModelInfo:
    model = STANDARD_REGISTRY.get(model_name)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    return model.model_info


@api_app.post("/v1/chat/completions")
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
        stream_response = await model.get_response(model_settings, True)
        return StreamingResponse(
            SSEEncoder(stream_response), media_type="text/event-stream"
        )
    else:
        model_response = await model.get_response(model_settings, False)
        return Response(
            content=model_response.model_dump_json(),
            media_type="application/json",
        )


@api_app.post("/v1/embeddings")
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
    model_response = await model.get_response(data)
    return model_response


@api_app.post("/v1/images/generations")
async def images_generations(
    data: ImageRequest, request: Request
) -> ImageResponse[ImageUrl] | ImageResponse[ImageB64]:
    model = STANDARD_REGISTRY.get(data.model)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    if not isinstance(model, ImageModel):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Model `{data.model}` is not an image generation model",
        )
    if data.response_format == "url":
        model_response_urls = await model.get_response(data, "url")
        for image in model_response_urls.data:
            image.url = str(request.base_url) + image.url
        return model_response_urls
    elif data.response_format == "b64_json":
        model_response_b64 = await model.get_response(data, "b64_json")
        return model_response_b64


@api_app.get("/private/images/{id_}.{ext}")
async def private(id_: str, ext: str) -> Response:
    data = get_data_from_image_id(id_)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    try:
        size, format_ = data.split("|")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    width, height = parse_dimensions(size)
    img = generate_noise_image_from_string(id_, width, height)
    buffer = io.BytesIO()
    img.save(buffer, format=format_)
    img_data = buffer.getvalue()
    return Response(content=img_data, media_type=f"image/{format_.lower()}")


@api_app.post("/v1/audio/speech")
async def speech_generation(data: SpeechRequest) -> Response:
    model = STANDARD_REGISTRY.get(data.model)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    if not isinstance(model, SpeechModel):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Model `{data.model}` is not a text to speech model",
        )
    audio_data = await model.get_response(data)
    return Response(
        content=audio_data,
        media_type=f"audio/{data.response_format}",
        headers={
            "Content-Length": str(len(audio_data)),
            "Accept-Ranges": "bytes",
        },
    )


from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import Mount


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    # Ensure the MCP session manager runs so StreamableHTTP has a task group
    # streamable_http_app() is called below which lazily creates the manager
    async with mcp.session_manager.run():
        yield


app = Starlette(
    routes=[
        # Expose the MCP Streamable HTTP server
        Mount("/mcp-servers/foo", app=mcp.streamable_http_app()),
        # Expose the REST API at the root path
        Mount("/", app=api_app),
    ],
    lifespan=lifespan,
)
