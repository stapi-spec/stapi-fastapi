import os

from fastapi import FastAPI
from mangum import Mangum

from stat_fastapi.api import StatApiRouter
from stat_fastapi.backend import StatApiBackend


def get_backend(name: str) -> StatApiBackend:
    if name == "landsat":
        from stat_fastapi_landsat import StatLandsatBackend

        return StatLandsatBackend()
    if name == "blacksky":
        from stat_fastapi_blacksky import BlackskyBackend

        return BlackskyBackend()
    if name == "up42":
        from stat_fastapi_up42 import StatUp42Backend

        return StatUp42Backend()
    if name == "umbra":
        from stat_fastapi_umbra import UmbraBackend

        return UmbraBackend()


app = FastAPI()
app.include_router(
    StatApiRouter(backend=get_backend(os.environ.get("BACKEND_NAME"))).router
)

handler = Mangum(app, lifespan="off")
