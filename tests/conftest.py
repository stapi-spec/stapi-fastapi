from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from typing import Any, Callable
from urllib.parse import urljoin

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import (
    Opportunity,
)
from stapi_fastapi.models.product import (
    Product,
)
from stapi_fastapi.routers.root_router import RootRouter

from .backends import (
    mock_get_order,
    mock_get_order_statuses,
    mock_get_orders,
)
from .shared import (
    InMemoryOrderDB,
    create_mock_opportunity,
    find_link,
    mock_product_test_satellite_provider,
    mock_product_test_spotlight,
)


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


@pytest.fixture
def mock_products() -> list[Product]:
    return [mock_product_test_spotlight, mock_product_test_satellite_provider]


@pytest.fixture
def mock_opportunities() -> list[Opportunity]:
    return [create_mock_opportunity()]


@pytest.fixture
def stapi_client(
    mock_products: list[Product],
    base_url: str,
    mock_opportunities: list[Opportunity],
) -> Iterator[TestClient]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
        try:
            yield {
                "_orders_db": InMemoryOrderDB(),
                "_opportunities": mock_opportunities,
            }
        finally:
            pass

    root_router = RootRouter(
        get_orders=mock_get_orders,
        get_order=mock_get_order,
        get_order_statuses=mock_get_order_statuses,
    )
    for mock_product in mock_products:
        root_router.add_product(mock_product)
    app = FastAPI(lifespan=lifespan)
    app.include_router(root_router, prefix="")

    with TestClient(app, base_url=f"{base_url}") as client:
        yield client


@pytest.fixture
def empty_stapi_client(base_url: str) -> Iterator[TestClient]:
    root_router = RootRouter(
        get_orders=mock_get_orders,
        get_order=mock_get_order,
        get_order_statuses=mock_get_order_statuses,
    )
    app = FastAPI()
    app.include_router(root_router, prefix="")

    with TestClient(app, base_url=f"{base_url}") as client:
        yield client


@pytest.fixture(scope="session")
def url_for(base_url: str) -> Iterator[Callable[[str], str]]:
    def with_trailing_slash(value: str) -> str:
        return value if value.endswith("/") else f"{value}/"

    def url_for(value: str) -> str:
        return urljoin(with_trailing_slash(base_url), f"./{value.lstrip('/')}")

    yield url_for


@pytest.fixture
def assert_link(url_for) -> Callable:
    def _assert_link(
        req: str,
        body: dict[str, Any],
        rel: str,
        path: str,
        media_type: str = "application/json",
    ):
        link = find_link(body["links"], rel)
        assert link, f"{req} Link[rel={rel}] should exist"
        assert link["type"] == media_type
        assert link["href"] == url_for(path)

    return _assert_link
