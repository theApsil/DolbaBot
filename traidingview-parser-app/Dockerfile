FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Установка зависимостей через uv
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen

# Копируем код
COPY . .

# Запуск FastAPI
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
