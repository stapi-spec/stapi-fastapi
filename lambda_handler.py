from importlib import import_module
from os import getenv

from fastapi import FastAPI
from mangum import Mangum

from stapi_fastapi.api import StapiRouter
from stapi_fastapi.backend import StapiBackend


def get_backend(import_name: str) -> StapiBackend:
    mod, attr = import_name.split(":", maxsplit=1)
    mod = import_module(mod)
    backend_class = getattr(mod, attr)
    return backend_class()


app = FastAPI()
app.include_router(
    StapiRouter(
        backend=get_backend(
            getenv(
                "BACKEND_NAME",
                "stapi_fastapi_landsat:LandsatBackend",
            )
        )
    ).router
)

handler = Mangum(app, lifespan="off")
