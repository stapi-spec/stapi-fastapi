from typing import Callable, Generator, TypeVar
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import Parser, fixture

from stapi_fastapi.api import StapiRouter
from stapi_fastapi_test_backend import TestBackend

T = TypeVar("T")

YieldFixture = Generator[T, None, None]


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--stapi-backend",
        action="store",
        default="stapi_fastapi_test_backend:TestBackend",
    )
    parser.addoption("--stapi-prefix", action="store", default="/stapi")
    parser.addoption("--stapi-product-id", action="store", default="mock:standard")


@fixture(scope="session")
def base_url() -> YieldFixture[str]:
    yield "http://stapiserver"


@fixture
def stapi_backend():
    yield TestBackend()


@fixture
def stapi_client(stapi_backend, base_url: str) -> YieldFixture[TestClient]:
    app = FastAPI()

    app.include_router(
        StapiRouter(backend=stapi_backend).router,
        prefix="",
    )

    yield TestClient(app, base_url=f"{base_url}")


@fixture(scope="session")
def url_for(base_url: str) -> YieldFixture[Callable[[str], str]]:
    def with_trailing_slash(value: str) -> str:
        return value if value.endswith("/") else f"{value}/"

    def url_for(value: str) -> str:
        return urljoin(with_trailing_slash(base_url), f"./{value.lstrip('/')}")

    yield url_for
