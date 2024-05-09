# Dockerized STAPI-FastAPI

The [Dockerfile](./Dockerfile) provides three targets:

- `base`: base install only, including poetry
- `dev`: base plus dev dependencies
- `lambda`: optimized for AWS Lambda, i.e. poetry removed

Both `dev` and `lambda` builds allow setting the backend class with the `BACKEND_NAME`
env var, i.e. `BACKEND_NAME=stapi_fastapi_landsat:LandsatBackend`.

For local dev use, it's recommended to use the docker compose file. The backend can
be choosen again by providing a env var `BACKEND_NAME`.
