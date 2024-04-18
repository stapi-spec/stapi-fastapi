from fastapi import FastAPI
from mangum import Mangum

from stat_fastapi.api import StatApiRouter
from stat_fastapi_landsat import StatLandsatBackend

app = FastAPI()
app.include_router(StatApiRouter(backend=StatLandsatBackend()).router)

handler = Mangum(app, lifespan="off")
