FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH"

RUN pip install --no-cache-dir --no-cache poetry

WORKDIR /app

COPY poetry.lock pyproject.toml .

RUN python3 -m venv /.venv && poetry install --no-cache --no-interaction --with lambda

COPY . /app
