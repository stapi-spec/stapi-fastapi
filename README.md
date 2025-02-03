# STAPI FastAPI - Sensor Tasking API with FastAPI

WARNING: The whole [STAPI spec] is very much a work in progress, so things are
guaranteed to be not correct.

## Usage

STAPI FastAPI provides an `fastapi.APIRouter` which must be included in
`fastapi.FastAPI` instance.

### Pagination

4 endpoints currently offer pagination:
`GET`: `'/orders`, `/products`, `/orders/{order_id}/statuses`
`POST`: `/opportunities`.

Pagination is token based and follows recommendations in the [STAC API pagination].
Limit and token are passed in as query params for `GET` endpoints, and via the body as
separate key/value pairs for `POST` requests.

If pagination is available and more records remain the response object will contain a
`next` link object that can be used to get the next page of results. No `next` `Link`
returned indicates there are no further records available.

`limit` defaults to 10 and maxes at 100.

## ADRs

ADRs can be found in in the [adrs](./adrs/README.md) directory.

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
[`./tests/application.py`](./tests/application.py). It can be run with
`uvicorn` as a way to interact with the API and to view the OpenAPI
documentation. Run it like so from the project root:

```commandline
uvicorn application:app --app-dir ./tests --reload
```

With the `uvicorn` defaults the app should be accessible at
`http://localhost:8000`.

### Implementing a backend

- The test suite assumes the backend can be instantiated without any parameters
  required by the constructor.

[STAPI spec]: https://github.com/stapi-spec/stapi-spec
[poetry]: https://python-poetry.org/
[STAC API pagination]: https://github.com/radiantearth/stac-api-spec/blob/release/v1.0.0/item-search/examples.md#paging-examples
