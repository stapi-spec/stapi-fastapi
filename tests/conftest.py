from collections.abc import Iterator
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
    Provider,
    ProviderRole,
)
from stapi_fastapi.routers.root_router import RootRouter

from .application import (
    TEST_STATUSES,
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
def order_db_statuses() -> InMemoryOrderDB:
    order_db = InMemoryOrderDB()
    order_db._statuses = TEST_STATUSES
    return order_db


@pytest.fixture
def product_backend(order_db: InMemoryOrderDB) -> MockProductBackend:
    return MockProductBackend(order_db)


@pytest.fixture
def root_backend(order_db: InMemoryOrderDB) -> MockRootBackend:
    return MockRootBackend(order_db)


@pytest.fixture
def root_backend_preloaded(order_db_statuses: InMemoryOrderDB) -> MockRootBackend:
    return MockRootBackend(order_db_statuses)


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


@pytest.fixture
def statuses_client(root_backend_preloaded, base_url: str) -> Iterator[TestClient]:
    root_router = RootRouter(root_backend_preloaded)
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


@pytest.fixture
def mock_test_spotlight_opportunities() -> list[Opportunity]:
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
                off_nadir={"minimum": 20, "maximum": 22},
                vehicle_id=[1],
                platform="platform_id",
                other_thing="abcd1234",
            ),
        ),
    ]
