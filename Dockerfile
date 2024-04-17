FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --no-cache poetry

COPY poetry.lock pyproject.toml /

RUN poetry install --no-cache --sync --no-interaction --with lambda && \
    rm poetry.lock pyproject.toml && \
    pip uninstall --yes poetry

COPY . /app
WORKDIR /app
