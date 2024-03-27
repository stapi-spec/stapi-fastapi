PYTEST_ADDOPTS := "--cov=stat_fastapi"

# List recipes
help:
    @just --list

# Bootstrap local repository checkout
bootstrap:
    poetry install --with dev
    poetry run pre-commit install

# Run test suite
test:
    poetry run pytest {{ PYTEST_ADDOPTS }}

# Run dev server
dev:
    poetry run dev
