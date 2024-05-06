import os

from fastapi import FastAPI
from mangum import Mangum

from stapi_fastapi.api import StapiRouter
from stapi_fastapi.backend import StapiBackend


def get_backend(name: str) -> StapiBackend:
    match name:
        case "landsat":
            from stapi_fastapi_landsat import LandsatBackend

            return LandsatBackend()
        case "blacksky":
            from stapi_fastapi_blacksky import BlackskyBackend

            return BlackskyBackend()
        case "up42":
            from stapi_fastapi_up42 import StatUp42Backend

            return StatUp42Backend()
        case "umbra":
            from stapi_fastapi_umbra import UmbraBackend

            return UmbraBackend()
        case _:
            raise TypeError("not a supported backend")


app = FastAPI()
app.include_router(
    StapiRouter(backend=get_backend(os.environ.get("BACKEND_NAME", "landsat"))).router
)

handler = Mangum(app, lifespan="off")
