from collections.abc import AsyncIterator, Generator, Iterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any, Callable
from urllib.parse import urljoin

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from stapi_fastapi.models.conformance import ASYNC_OPPORTUNITIES, CORE, OPPORTUNITIES
from stapi_fastapi.models.opportunity import (
    Opportunity,
)
from stapi_fastapi.models.product import (
    Product,
)
from stapi_fastapi.routers.root_router import RootRouter

from .backends import (
    mock_get_opportunity_search_record,
    mock_get_opportunity_search_records,
    mock_get_order,
    mock_get_order_statuses,
    mock_get_orders,
)
from .shared import (
    InMemoryOpportunityDB,
    InMemoryOrderDB,
    create_mock_opportunity,
    find_link,
    product_test_satellite_provider_sync_opportunity,
    product_test_spotlight_sync_opportunity,
)
from .test_datetime_interval import rfc3339_strftime


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


@pytest.fixture
def mock_products(request) -> list[Product]:
    if request.node.get_closest_marker("mock_products") is not None:
        return request.node.get_closest_marker("mock_products").args[0]
    return [
        product_test_spotlight_sync_opportunity,
        product_test_satellite_provider_sync_opportunity,
    ]


@pytest.fixture
def mock_opportunities() -> list[Opportunity]:
    return [create_mock_opportunity()]


@pytest.fixture
def stapi_client(
    mock_products: list[Product],
    base_url: str,
    mock_opportunities: list[Opportunity],
) -> Generator[TestClient, None, None]:
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
        conformances=[CORE],
    )

    for mock_product in mock_products:
        root_router.add_product(mock_product)

    app = FastAPI(lifespan=lifespan)
    app.include_router(root_router, prefix="")

    with TestClient(app, base_url=f"{base_url}") as client:
        yield client


@pytest.fixture
def stapi_client_async_opportunity(
    mock_products: list[Product],
    base_url: str,
    mock_opportunities: list[Opportunity],
) -> Generator[TestClient, None, None]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
        try:
            yield {
                "_orders_db": InMemoryOrderDB(),
                "_opportunities_db": InMemoryOpportunityDB(),
                "_opportunities": mock_opportunities,
            }
        finally:
            pass

    root_router = RootRouter(
        get_orders=mock_get_orders,
        get_order=mock_get_order,
        get_order_statuses=mock_get_order_statuses,
        get_opportunity_search_records=mock_get_opportunity_search_records,
        get_opportunity_search_record=mock_get_opportunity_search_record,
        conformances=[CORE, OPPORTUNITIES, ASYNC_OPPORTUNITIES],
    )

    for mock_product in mock_products:
        root_router.add_product(mock_product)

    app = FastAPI(lifespan=lifespan)
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
        method: str | None = None,
    ):
        link = find_link(body["links"], rel)
        assert link, f"{req} Link[rel={rel}] should exist"
        assert link["type"] == media_type
        assert link["href"] == url_for(path)
        if method:
            assert link["method"] == method

    return _assert_link


@pytest.fixture
def limit() -> int:
    return 10


@pytest.fixture
def opportunity_search(limit) -> dict[str, Any]:
    now = datetime.now(UTC)
    end = now + timedelta(days=5)
    format = "%Y-%m-%dT%H:%M:%S.%f%z"
    start_string = rfc3339_strftime(now, format)
    end_string = rfc3339_strftime(end, format)

    return {
        "geometry": {
            "type": "Point",
            "coordinates": [0, 0],
        },
        "datetime": f"{start_string}/{end_string}",
        "filter": {
            "op": "and",
            "args": [
                {"op": ">", "args": [{"property": "off_nadir"}, 0]},
                {"op": "<", "args": [{"property": "off_nadir"}, 45]},
            ],
        },
        "limit": limit,
    }
