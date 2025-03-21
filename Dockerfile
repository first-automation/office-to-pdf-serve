FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y libreoffice fonts-ipafont-gothic fonts-ipafont-mincho python3 python3-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV LANG=ja_JP.UTF-8
WORKDIR /app

COPY . .

RUN uv sync --frozen --no-cache

