from importlib import import_module
from typing import Callable, Generator, TypeVar
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import MonkeyPatch, Parser, fixture

from stat_fastapi.api import StatApiRouter

T = TypeVar("T")

YieldFixture = Generator[T, None, None]


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--stat-backend",
        action="store",
        default="stat_fastapi_mock_backend:StatMockBackend",
    )
    parser.addoption("--stat-prefix", action="store", default="/stat")
    parser.addoption("--stat-product-id", action="store", default="mock:standard")


@fixture(scope="session")
def product_id(request) -> YieldFixture[str]:
    yield request.config.getoption("--stat-product-id")


@fixture(scope="session")
def base_url() -> YieldFixture[str]:
    yield "http://statserver"


@fixture(scope="session")
def router_prefix(request) -> YieldFixture[str]:
    prefix = request.config.getoption("--stat-prefix").rstrip("/").strip()
    prefix = prefix if prefix != "/" else ""
    yield prefix


@fixture
def stat_client(
    request, monkeypatch: MonkeyPatch, base_url: str, router_prefix: str
) -> YieldFixture[TestClient]:
    app = FastAPI()

    module, backend = request.config.getoption("--stat-backend").split(":", 1)
    monkeypatch.setenv("DATABASE", "sqlite://")
    module = import_module(module)
    backend = getattr(module, backend)()

    app.include_router(
        StatApiRouter(backend=backend).router,
        prefix=router_prefix,
    )

    yield TestClient(app, base_url=f"{base_url}{router_prefix}")


@fixture(scope="session")
def url_for(base_url: str, router_prefix: str) -> YieldFixture[Callable[[str], str]]:
    def with_trailing_slash(value: str) -> str:
        return value if value.endswith("/") else f"{value}/"

    def url_for(value: str) -> str:
        prefixed_path = urljoin(
            with_trailing_slash(router_prefix), f"./{value.lstrip('/')}"
        )
        return urljoin(with_trailing_slash(base_url), f"./{prefixed_path.lstrip('/')}")

    yield url_for
