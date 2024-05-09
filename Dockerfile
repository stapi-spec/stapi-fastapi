FROM python:3.12-slim AS base

ENV PATH="/venv/bin:/opt/poetry/bin:$PATH" \
    POETRY_VIRTUALENVS_CREATE=0 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv

RUN python3 -m venv /opt/poetry && \
    /opt/poetry/bin/pip3 install --no-cache-dir --no-cache poetry

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    python3 -m venv /venv && \
    poetry install --no-interaction --compile && \
    python3 -m compileall stapi_fastapi
COPY . /app


FROM base AS dev

RUN --mount=type=cache,target=/root/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    poetry install --no-interaction --with dev --compile

ENV HOST=0.0.0.0

CMD [ "/opt/poetry/bin/poetry", "run", "dev" ]

FROM base AS lambda-builder

RUN --mount=type=cache,target=/root/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    poetry install --no-interaction --with lambda --compile


FROM python:3.12-slim AS lambda

ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv

WORKDIR /app
COPY --from=lambda-builder /app /app
COPY --from=lambda-builder /venv /venv

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD ["lambda_handler.handler"]
