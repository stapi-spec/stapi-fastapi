from typing import Callable, Generator, TypeVar
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import Parser, fixture

from stat_fastapi.api import StatApiRouter
from stat_fastapi_test_backend import TestBackend

T = TypeVar("T")

YieldFixture = Generator[T, None, None]


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--stat-backend",
        action="store",
        default="stat_fastapi_test_backend:TestBackend",
    )
    parser.addoption("--stat-prefix", action="store", default="/stat")
    parser.addoption("--stat-product-id", action="store", default="mock:standard")


@fixture(scope="session")
def base_url() -> YieldFixture[str]:
    yield "http://statserver"


@fixture
def stat_backend():
    yield TestBackend()


@fixture
def stat_client(stat_backend, base_url: str) -> YieldFixture[TestClient]:
    app = FastAPI()

    app.include_router(
        StatApiRouter(backend=stat_backend).router,
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
