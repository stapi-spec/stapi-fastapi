from collections.abc import Iterator
from typing import Any, Callable
from urllib.parse import urljoin

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from httpx import Response

from stapi_fastapi.models.product import (
    Product,
    Provider,
    ProviderRole,
)
from stapi_fastapi.routers.root_router import RootRouter

from .application import (
    InMemoryOrderDB,
    MockProductBackend,
    MockRootBackend,
    MyOpportunityProperties,
    MyOrderParameters,
    MyProductConstraints,
)
from .shared import find_link


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


@pytest.fixture
def order_db() -> InMemoryOrderDB:
    return InMemoryOrderDB()


@pytest.fixture
def product_backend(order_db: InMemoryOrderDB) -> MockProductBackend:
    return MockProductBackend(order_db)


@pytest.fixture
def root_backend(order_db: InMemoryOrderDB) -> MockRootBackend:
    return MockRootBackend(order_db)


@pytest.fixture
def mock_product_test_spotlight(
    product_backend: MockProductBackend, mock_provider: Provider
) -> Product:
    """Fixture for a mock Test Spotlight product."""
    return Product(
        id="test-spotlight",
        title="Test Spotlight Product",
        description="Test product for test spotlight",
        license="CC-BY-4.0",
        keywords=["test", "satellite"],
        providers=[mock_provider],
        links=[],
        constraints=MyProductConstraints,
        opportunity_properties=MyOpportunityProperties,
        order_parameters=MyOrderParameters,
        backend=product_backend,
    )


@pytest.fixture
def mock_product_test_wolf_cola(
    product_backend: MockProductBackend, mock_provider: Provider
) -> Product:
    """Fixture for a mock Wolf Cola product."""
    return Product(
        id="test-wolf-cola",
        title="Test Wolf Cola Product",
        description="Test product for Wolf Cola for testing GET /product pagination",
        license="CC-BY-4.0",
        keywords=["test", "satellite", "wolf-cola"],
        providers=[mock_provider],
        links=[],
        constraints=MyProductConstraints,
        opportunity_properties=MyOpportunityProperties,
        order_parameters=MyOrderParameters,
        backend=product_backend,
    )


@pytest.fixture
def stapi_client(
    root_backend,
    mock_product_test_spotlight,
    mock_product_test_wolf_cola,
    base_url: str,
) -> Iterator[TestClient]:
    root_router = RootRouter(root_backend)
    root_router.add_product(mock_product_test_spotlight)
    root_router.add_product(mock_product_test_wolf_cola)
    app = FastAPI()
    app.include_router(root_router, prefix="")

    with TestClient(app, base_url=f"{base_url}") as client:
        yield client


@pytest.fixture
def empty_stapi_client(root_backend, base_url: str) -> Iterator[TestClient]:
    root_router = RootRouter(root_backend)
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
def products(mock_product_test_spotlight: Product) -> list[Product]:
    return [mock_product_test_spotlight]


@pytest.fixture
def mock_provider() -> Provider:
    return Provider(
        name="Test Provider",
        description="A provider for Test data",
        roles=[ProviderRole.producer],  # Example role
        url="https://test-provider.example.com",  # Must be a valid URL
    )


def pagination_tester(
    stapi_client: TestClient,
    endpoint: str,
    method: str,
    limit: int,
    target: str,
    expected_total_returns: int,
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
        res = make_request(stapi_client, next_url, method, body, next_url, limit)
        assert res.status_code == status.HTTP_200_OK
        assert len(resp_body[target]) <= limit
        resp_body = res.json()
        retrieved.extend(resp_body[target])

        if resp_body["links"]:
            next_url = next(
                (d["href"] for d in resp_body["links"] if d["rel"] == "next"), None
            )
        else:
            next_url = None

    assert len(retrieved) == expected_total_returns


def make_request(
    stapi_client: TestClient,
    endpoint: str,
    method: str,
    body: dict | None,
    next_token: str | None,
    limit: int,
) -> Response:
    """request wrapper for pagination tests"""
    if next_token and "next=" in next_token:
        next_token = next_token.split("next=")[1]
    params = {"next": next_token, "limit": limit}

    if method == "GET":
        res = stapi_client.get(endpoint, params=params)
    if method == "POST":
        res = stapi_client.post(endpoint, json=body, params=params)

    return res
