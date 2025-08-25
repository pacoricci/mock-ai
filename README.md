# Mock AI Service

This project provides a lightweight FastAPI application that mimics common AI endpoints for development and testing purposes.

It supports chat completions, embedding generation, image generation, text-to-speech and listing available models. The server returns deterministic placeholder results that allow client implementations to be exercised without contacting a real model provider.

## Installation

The service requires Python 3.12 or newer. Install the package from the repository root using pip:

```bash
pip install .
```

## Running the server

The package installs a command line tool `mock-ai` which exposes two modes:

- `mock-ai dev` – start the server in development mode with auto reload enabled on port 5001
- `mock-ai run` – start a production server. Extra uvicorn options can be supplied as flags

For example to serve locally for development:

```bash
mock-ai dev --port 8000
```

By default the API will be available at [http://127.0.0.1:5001](http://127.0.0.1:5001) (or the host and port you choose). The OpenAPI docs for the REST API are served at `/docs`.

## Usage

Once running, the service exposes endpoints under `/v1` that mirror typical AI APIs. Use any HTTP client to interact with it. For instance:

- `POST /v1/chat/completions` for chat responses
- `POST /v1/embeddings` for embeddings
- `POST /v1/images/generations` for test images
- `POST /v1/audio/speech` for text-to-speech
- `GET /v1/models` to list registered models

Each endpoint returns deterministic content suitable for automated tests or demos without an actual model backend.

## MCP (Streamable HTTP)

The service also exposes an MCP server using Streamable HTTP for tool calls.

- Endpoint: `POST http://127.0.0.1:5001/mcp-servers/foo/mcp/`
- Mode: stateless requests (no session persistence required)
- Client: use an MCP client that supports the Streamable HTTP transport

Note: The MCP transport is not part of the REST OpenAPI schema and won’t appear in `/docs`.

## Authentication

Set allowed bearer tokens with the `AUTH_BEARER_TOKENS` environment variable. Tokens
can be supplied as a comma-separated list or by repeating the variable. Every
request must include a matching `Authorization: Bearer <token>` header.

Example:

```bash
export AUTH_BEARER_TOKENS=token1,token2
# or
export AUTH_BEARER_TOKENS=token1
export AUTH_BEARER_TOKENS=token2
```

## CORS configuration

Cross-Origin Resource Sharing (CORS) can be configured via environment variables.
By default all origins, methods and headers are allowed. The main variables are:

- `CORS_ALLOW_ORIGINS` – comma separated list of allowed origins (defaults to `*`)
- `CORS_ALLOW_CREDENTIALS` – whether to allow credentials (defaults to `true`)
- `CORS_ALLOW_METHODS` – comma separated list of allowed HTTP methods (defaults to `*`)
- `CORS_ALLOW_HEADERS` – comma separated list of allowed request headers (defaults to `*`)

For example to only allow requests from `http://localhost:3000`:

```bash
export CORS_ALLOW_ORIGINS=http://localhost:3000
```
