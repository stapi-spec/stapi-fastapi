FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --no-cache poetry

WORKDIR /app

COPY poetry.lock pyproject.toml .

RUN poetry install --no-cache --no-interaction --with lambda

COPY . /app
