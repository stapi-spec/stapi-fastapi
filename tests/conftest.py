from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from urllib.parse import urljoin
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from geojson_pydantic.types import Position2D
from httpx import Response
from pytest import fail

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
    MyOrderParameters,
    MyProductConstraints,
    OffNadirRange,
    mock_create_order,
    mock_get_order,
    mock_get_order_statuses,
    mock_get_orders,
    mock_product_test_spotlight,
    mock_search_opportunities,
    provider,
)
from .shared import find_link


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


mock_product_test_satellite_provider = Product(
    id="test-satellite-provider",
    title="Satellite Product",
    description="A product by a satellite provider",
    license="CC-BY-4.0",
    keywords=["test", "satellite", "provider"],
    providers=[provider],
    links=[],
    create_order=mock_create_order,
    search_opportunities=mock_search_opportunities,
    constraints=MyProductConstraints,
    opportunity_properties=MyOpportunityProperties,
    order_parameters=MyOrderParameters,
)


@pytest.fixture
def mock_products() -> list[Product]:
    return [mock_product_test_spotlight, mock_product_test_satellite_provider]


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


def pagination_tester(
    stapi_client: TestClient,
    endpoint: str,
    method: str,
    limit: int,
    target: str,
    expected_returns: list,
    body: dict | None = None,
) -> None:
    retrieved = []

    res = make_request(stapi_client, endpoint, method, body, None, limit)
    assert res.status_code == status.HTTP_200_OK
    resp_body = res.json()

    assert len(resp_body[target]) <= limit
    retrieved.extend(resp_body[target])
    next_url = next((d["href"] for d in resp_body["links"] if d["rel"] == "next"), None)

    while next_url:
        url = next_url
        if method == "POST":
            body = next(
                (d["body"] for d in resp_body["links"] if d["rel"] == "next"), None
            )

        res = make_request(stapi_client, url, method, body, next_url, limit)
        assert res.status_code == status.HTTP_200_OK
        assert len(resp_body[target]) <= limit
        resp_body = res.json()
        retrieved.extend(resp_body[target])

        # get url w/ query params for next call if exists, and POST body if necessary
        if resp_body["links"]:
            next_url = next(
                (d["href"] for d in resp_body["links"] if d["rel"] == "next"), None
            )
        else:
            next_url = None

    assert len(retrieved) == len(expected_returns)
    assert retrieved == expected_returns


def make_request(
    stapi_client: TestClient,
    endpoint: str,
    method: str,
    body: dict | None,
    next_token: str | None,
    limit: int,
) -> Response:
    """request wrapper for pagination tests"""

    match method:
        case "GET":
            if next_token:  # extract pagination token
                next_token = next_token.split("next=")[1]
            params = {"next": next_token, "limit": limit}
            res = stapi_client.get(endpoint, params=params)
        case "POST":
            res = stapi_client.post(endpoint, json=body)
        case _:
            fail(f"method {method} not supported in make request")

    return res
