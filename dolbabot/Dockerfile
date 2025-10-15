FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["uv", "run", "python", "main.py"]