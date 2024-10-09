from typing import Callable, Generator, TypeVar, List
from urllib.parse import urljoin
from uuid import uuid4
import pytest
from datetime import datetime, timezone, timedelta, UTC
from geojson_pydantic import Point
from pytest import Parser, fixture

from stapi_fastapi.models.product import Product, Provider, ProviderRole
from stapi_fastapi.models.shared import Link
from stapi_fastapi.models.opportunity import OpportunityProperties, Opportunity, OpportunityRequest
from stapi_fastapi.types.datetime_interval import DatetimeInterval

from collections.abc import Iterator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from stapi_fastapi.products_router import ProductRouter

from .backend import TestBackend


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


@pytest.fixture
def stapi_backend() -> Iterator[TestBackend]:
    yield TestBackend()

@pytest.fixture
def mock_product_umbra_spotlight(mock_provider_umbra: Provider) -> Product:
    """Fixture for a mock Umbra Spotlight product."""

    return Product(
        id=str(uuid4()),
        title="Umbra Spotlight Product",
        description="Test product for umbra spotlight",
        license="CC-BY-4.0",
        keywords=["test", "umbra", "satellite"],
        providers=[mock_provider_umbra],
        links=[
            Link(href="http://example.com", rel="self"),
            Link(href="http://example.com/catalog", rel="parent"),
        ],
        parameters=UmbraSpotlightProperties
    )

@pytest.fixture
def stapi_client(stapi_backend, base_url: str) -> Iterator[TestClient]:
    app = FastAPI()

    app.include_router(
        ProductRouter(mock_product_umbra_spotlight),
        prefix="",
    )

    yield TestClient(app, base_url=f"{base_url}")


@pytest.fixture(scope="session")
def url_for(base_url: str) -> Iterator[Callable[[str], str]]:
    def with_trailing_slash(value: str) -> str:
        return value if value.endswith("/") else f"{value}/"

    def url_for(value: str) -> str:
        return urljoin(with_trailing_slash(base_url), f"./{value.lstrip('/')}")

    yield url_for


@pytest.fixture
def products() -> Iterator[list[Product]]:
    class Parameters(BaseModel):
        pass

    yield [
        Product(
            id="mock:standard",
            description="Mock backend's standard product",
            license="CC0-1.0",
            providers=[
                Provider(
                    name="ACME",
                    roles=[
                        ProviderRole.licensor,
                        ProviderRole.producer,
                        ProviderRole.processor,
                        ProviderRole.host,
                    ],
                    url="http://acme.example.com",
                )
            ],
            parameters=Parameters,
            links=[],
        )
    ]


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
def allowed_payloads(products: list[Product]) -> Iterator[list[OpportunityRequest]]:
    yield [
        OpportunityRequest(
            geometry=Point(type="Point", coordinates=[13.4, 52.5]),
            product_id=products[0].id,
            datetime=(datetime.now(UTC), datetime.now(UTC)),
            filter={},
        ),
    ]

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


@fixture(scope="session")
def url_for(base_url: str) -> YieldFixture[Callable[[str], str]]:
    def with_trailing_slash(value: str) -> str:
        return value if value.endswith("/") else f"{value}/"

    def url_for(value: str) -> str:
        return urljoin(with_trailing_slash(base_url), f"./{value.lstrip('/')}")

    yield url_for

@pytest.fixture
def mock_provider_umbra() -> Provider:
    return Provider(
        name="Umbra Provider",
        description="A provider for Umbra data",
        roles=[ProviderRole.producer],  # Example role
        url="https://umbra-provider.example.com"  # Must be a valid URL
    )

# Define a mock OpportunityProperties class for Umbra
class UmbraSpotlightProperties(OpportunityProperties):
    datetime: DatetimeInterval

@pytest.fixture
def mock_products(mock_product_umbra_spotlight: Product) -> List[Product]:
    """Fixture to return a list of mock products."""
    return [mock_product_umbra_spotlight]

@pytest.fixture
def mock_umbra_spotlight_opportunities() -> List[Opportunity]:
    """Fixture to create mock data for Opportunities for `umbra-spotlight-1`."""
    now = datetime.now(timezone.utc)  # Use timezone-aware datetime
    start = now
    end = start + timedelta(days=5)
    datetime_interval = f"{start.isoformat()}/{end.isoformat()}"

    # Create a list of mock opportunities for the given product
    return [
        Opportunity(
            id=str(uuid4()),
            type="Feature",
            geometry=Point(type="Point", coordinates=[0, 0]),  # Simple point geometry
            properties=UmbraSpotlightProperties(
                datetime=datetime_interval,
                off_nadir=20,
            ),
        ),
    ]