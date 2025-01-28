from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from urllib.parse import urljoin
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from geojson_pydantic.types import Position2D

from stapi_fastapi.models.opportunity import (
    Opportunity,
)
from stapi_fastapi.models.product import (
    Product,
)
from stapi_fastapi.routers.root_router import RootRouter

from .application import (
    InMemoryOrderDB,
    MyOpportunityProperties,
    OffNadirRange,
    mock_get_order,
    mock_get_order_statuses,
    mock_get_orders,
    product,
)
from .shared import find_link


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


@pytest.fixture
def mock_product() -> Product:
    """Fixture for a mock Test Spotlight product."""
    return product


@pytest.fixture
def stapi_client(
    mock_product,
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
    ):
        link = find_link(body["links"], rel)
        assert link, f"{req} Link[rel={rel}] should exist"
        assert link["type"] == media_type
        assert link["href"] == url_for(path)

    return _assert_link


@pytest.fixture
def mock_opportunities() -> list[Opportunity]:
    """Fixture to create mock data for Opportunities for `test-spotlight-1`."""
    now = datetime.now(timezone.utc)  # Use timezone-aware datetime
    start = now
    end = start + timedelta(days=5)

    # Create a list of mock opportunities for the given product
    return [
        Opportunity(
            id=str(uuid4()),
            type="Feature",
            geometry=Point(
                type="Point",
                coordinates=Position2D(longitude=0.0, latitude=0.0),
            ),
            properties=MyOpportunityProperties(
                product_id="xyz123",
                datetime=(start, end),
                off_nadir=OffNadirRange(minimum=20, maximum=22),
                vehicle_id=[1],
                platform="platform_id",
                other_thing="abcd1234",
            ),
        ),
    ]
