import os

from fastapi import FastAPI
from mangum import Mangum

from stat_fastapi.api import StatApiRouter
from stat_fastapi.backend import StatApiBackend


def get_backend(name: str) -> StatApiBackend:
    match name:
        case "landsat":
            from stat_fastapi_landsat import StatLandsatBackend

            return StatLandsatBackend()
        case "blacksky":
            from stat_fastapi_blacksky import BlackskyBackend

            return BlackskyBackend()
        case "up42":
            from stat_fastapi_up42 import StatUp42Backend

            return StatUp42Backend()
        case "umbra":
            from stat_fastapi_umbra import UmbraBackend

            return UmbraBackend()
        case _:
            raise TypeError("not a supported backend")


app = FastAPI()
app.include_router(
    StatApiRouter(backend=get_backend(os.environ.get("BACKEND_NAME", "landsat"))).router
)

handler = Mangum(app, lifespan="off")
