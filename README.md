# STAPI FastAPI - Sensor Tasking API with FastAPI

WARNING: The whole [STAPI spec](https://github.com/stapi-spec/stapi-spec) is very much work in progress, so things are
guaranteed to be not correct.

NOTE: This repository uses [scripts to rule them all](https://github.com/github/scripts-to-rule-them-all)

## Usage

STAPI FastAPI provides an `fastapi.APIRouter` which must be included in
`fastapi.FastAPI` instance.

## Development

It's 2024 and we still need to pick our poison for a 2024 dependency management
solution. This project picks [poetry][poetry] for now.

The mock backend uses SQLite/Spatialite as storage, therefore the
`SPATIALITE_LIBRARY_PATH` env var must be set to load the spatialite extension:

```bash
export DATABASE=sqlite:///order.sqlite
export SPATIALITE_LIBRARY_PATH=/path/to/mod_spatialite.dylib
```

Also see [DOCKER.md](./DOCKER.md) for details on docker setup for and deployment.

### Dev Setup

Setup is managed with `poetry` and `pre-commit`, all of which can be initialised
by `./scripts/bootstrap`.

### Test Suite

A `pytest` based test suite is provided. Run it as `./scripts/test`. Any additional
pytest flags are passed along

### Dev Server

For dev purposes, [stapi_fastapi.**dev**.py](./stapi_fastapi/__dev__.py) shows
a minimal demo with `uvicorn` to run the full app. Start it with `./scripts/server`.
Choose backend with `BACKEND_NAME` env var, defaults to Landsat backend.

### Implementing a backend

- The test suite assumes the backend can be instantiated without any parameters
  required by the constructor.

[poetry]: https://python-poetry.org/
