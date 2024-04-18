FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH" \
    DEBIAN_FRONTEND=noninteractive

RUN pip install --no-cache-dir --no-cache poetry

WORKDIR /app

COPY poetry.lock pyproject.toml .

RUN python3 -m venv /.venv && poetry install --no-cache --no-interaction --with lambda
RUN apt-get -yq update && apt-get -yq install git && pip install \
    git+https://github.com/stat-utils/stat-fastapi-up42.git@main \
    git+https://github.com/stat-utils/stat-fastapi-blacksky.git@main \
    git+https://github.com/stat-utils/stat-fastapi-umbra.git@main \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN poetry run python -c "import compileall; compileall.compile_path(maxlevels=10)" && poetry run python -m compileall stat_fastapi
