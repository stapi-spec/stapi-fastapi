from fastapi import FastAPI
from mangum import Mangum

from stat_fastapi.api import StatApiRouter
from stat_fastapi_test_backend import TestBackend

app = FastAPI()
app.include_router(StatApiRouter(backend=TestBackend()).router)

handler = Mangum(app, lifespan="off")
