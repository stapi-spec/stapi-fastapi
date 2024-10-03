from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Callable
from urllib.parse import urljoin

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from pydantic import BaseModel
from stapi_fastapi.api import StapiRouter
from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.product import Product, Provider, ProviderRole

from .backend import TestBackend


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    yield "http://stapiserver"


@pytest.fixture
def stapi_backend() -> Iterator[TestBackend]:
    yield TestBackend()


@pytest.fixture
def stapi_client(stapi_backend, base_url: str) -> Iterator[TestClient]:
    app = FastAPI()

    app.include_router(
        StapiRouter(backend=stapi_backend).router,
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
