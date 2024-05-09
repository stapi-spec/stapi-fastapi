#!/usr/bin/env python3

from importlib import import_module
from sys import stderr

from fastapi import FastAPI
from pydantic import field_validator

try:
    from pydantic_settings import BaseSettings
    from uvicorn.main import run
except ImportError:
    print("install uvicorn and pydantic-settings to use the dev server", file=stderr)
    exit(1)

from stapi_fastapi.api import StapiRouter


class DevSettings(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"
    backend_name: str = "stapi_fastapi_landsat:LandsatBackend"

    @field_validator("backend_name", mode="after")
    def validate_backend(cls, value: str):
        try:
            mod, attr = value.split(":", maxsplit=1)
            mod = import_module(mod)
            attr = getattr(mod, attr)
        except ImportError as exc:
            raise ValueError("not a valid backend") from exc
        return attr


settings = DevSettings()
backend = settings.backend_name()
app = FastAPI(debug=True)
app.include_router(StapiRouter(backend).router)


def cli():
    run(
        "stapi_fastapi.__dev__:app", reload=True, host=settings.host, port=settings.port
    )
