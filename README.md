# STAPI FastAPI - Sensor Tasking API with FastAPI

WARNING: The whole [STAPI spec] is very much work in progress, so things are
guaranteed to be not correct.

## Usage

STAPI FastAPI provides an `fastapi.APIRouter` which must be included in
`fastapi.FastAPI` instance.

## Development

It's 2024 and we still need to pick our poison for a 2024 dependency management
solution. This project picks [poetry] for now.

### Dev Setup

Setup is managed with `poetry` and `pre-commit`. It's recommended to install
the project into a virtual environment. Bootstrapping a development environment
could look something like this:

```commandline
python -m venv .venv
source .venv/bin/activate
pip install poetry  # if not already installed to the system
poetry install --with dev
pre-commit install
```

### Test Suite

A `pytest` based test suite is provided, and can be run simply using the
command `pytest`.

### Dev Server

This project cannot be run on its own because it does not have any backend
implementations. However, a minimal test implementation is provided in
[`./bin/server.py`](./bin/server.py). It can be run with `uvicorn` as a way to
interact with the API and to view the OpenAPI documentation. Run it like so
from the project root:

```commandline
uvicorn server:app --app-dir ./bin --reload
```

With the `uvicorn` defaults the app should be accessible at
`http://localhost:8000`.

### Implementing a backend

- The test suite assumes the backend can be instantiated without any parameters
  required by the constructor.

[STAPI spec]: https://github.com/stapi-spec/stapi-spec
[poetry]: https://python-poetry.org/
