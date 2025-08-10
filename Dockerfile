FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && apt install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY mock_ai /app/mock_ai

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

EXPOSE 5001

CMD ["mock-ai", "run", "--port", "5001", "--workers", "4"]
