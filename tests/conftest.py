from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone
from typing import Callable, List
from urllib.parse import urljoin
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from geojson_pydantic.types import Position2D
from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityPropertiesBase,
)
from stapi_fastapi.models.product import Product, Provider, ProviderRole
from stapi_fastapi.routers.root_router import RootRouter

from .backend import TestProductBackend, TestRootBackend


class TestSpotlightProperties(OpportunityPropertiesBase):
    off_nadir: int


@pytest.fixture
def mock_product_test_spotlight(mock_provider_test: Provider) -> Product:
    """Fixture for a mock Test Spotlight product."""
    return Product(
        id="test-spotlight",
        title="Test Spotlight Product",
        description="Test product for test spotlight",
        license="CC-BY-4.0",
        keywords=["test", "satellite"],
        providers=[mock_provider_test],
        links=[],
        constraints=TestSpotlightProperties,
        backend=TestProductBackend(),
    )


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


@pytest.fixture
def product_backend() -> Iterator[TestProductBackend]:
    yield TestProductBackend()


@pytest.fixture
def root_backend() -> Iterator[TestRootBackend]:
    yield TestRootBackend()


@pytest.fixture
def stapi_client(
    root_backend, mock_product_test_spotlight, base_url: str
) -> Iterator[TestClient]:
    root_router = RootRouter(root_backend)
    root_router.add_product(mock_product_test_spotlight)
    app = FastAPI()
    app.include_router(root_router, prefix="")

    yield TestClient(app, base_url=f"{base_url}")


@pytest.fixture(scope="session")
def url_for(base_url: str) -> Iterator[Callable[[str], str]]:
    def with_trailing_slash(value: str) -> str:
        return value if value.endswith("/") else f"{value}/"

    def url_for(value: str) -> str:
        return urljoin(with_trailing_slash(base_url), f"./{value.lstrip('/')}")

    yield url_for


@pytest.fixture
def products(mock_product_test_spotlight) -> list[Product]:
    return [mock_product_test_spotlight]


@pytest.fixture
def opportunities(products: list[Product]) -> Iterator[list[Opportunity]]:
    yield [
        Opportunity(
            geometry=Point(type="Point", coordinates=[13.4, 52.5]),
            properties={
                "product_id": products[0].id,
                "datetime": (datetime.now(UTC), datetime.now(UTC)),
                "filter": {},
            },
        )
    ]


@pytest.fixture
def mock_provider_test() -> Provider:
    return Provider(
        name="Test Provider",
        description="A provider for Test data",
        roles=[ProviderRole.producer],  # Example role
        url="https://test-provider.example.com",  # Must be a valid URL
    )


@pytest.fixture
def mock_test_spotlight_opportunities() -> List[Opportunity]:
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
            properties=TestSpotlightProperties(
                datetime=(start, end),
                off_nadir=20,
            ),
        ),
    ]
