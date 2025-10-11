FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]