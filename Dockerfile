FROM python:3.12-slim

ARG VENV=/.venv

ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=$VENV \
    POETRY_VIRTUALENVS_CREATE=0 \
    PATH="/.venv/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV && pip install --no-cache-dir --no-cache poetry

COPY poetry.lock pyproject.toml /

RUN poetry install --no-cache --sync --no-interaction --with lambda && \
    rm poetry.lock pyproject.toml && \
    pip uninstall --yes poetry

COPY . /app
WORKDIR /app
