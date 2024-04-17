from datetime import UTC, datetime

from geojson_pydantic import Point
from pydantic import BaseModel
from pytest import fixture

from stat_fastapi.models.opportunity import Opportunity, OpportunitySearch
from stat_fastapi.models.product import Product, Provider, ProviderRole


@fixture
def products():
    class Constraints(BaseModel):
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
            constraints=Constraints,
            links=[],
        )
    ]


@fixture
def opportunities(products: list[Product]):
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


@fixture
def allowed_payloads(products: list[Product]):
    yield [
        OpportunitySearch(
            geometry=Point(type="Point", coordinates=[13.4, 52.5]),
            product_id=products[0].id,
            datetime=(datetime.now(UTC), datetime.now(UTC)),
            filter={},
        ),
    ]
