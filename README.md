# STAPI FastAPI - Sensor Tasking API with FastAPI

WARNING: The whole [STAPI spec](https://github.com/stapi-spec/stapi-spec) is
very much work in progress, so things are guaranteed to be not correct.

## Usage

STAPI FastAPI provides an `fastapi.APIRouter` which must be included in
`fastapi.FastAPI` instance.

## Development

It's 2024 and we still need to pick our poison for a 2024 dependency management
solution. This project picks [poetry][poetry] for now.

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
implementations. If a development server is desired, run one of the
implementations such as
[stapi-fastapi-tle](https://github.com/stapi-spec/stapi-fastapi-tle). To test
something like stapi-fastapi-tle with your development version of
stapi-fastapi, install them both into the same virtual environment.

### Implementing a backend

- The test suite assumes the backend can be instantiated without any parameters
  required by the constructor.

[poetry]: https://python-poetry.org/
