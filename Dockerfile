FROM ubuntu:24.04

RUN apt-get update && apt-get install -y libreoffice python3 python3-pip && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY . .

RUN uv sync --frozen --no-cache

CMD ["/app/.venv/bin/fastapi", "run", "app.py", "--port", "8000", "--host", "0.0.0.0"]
