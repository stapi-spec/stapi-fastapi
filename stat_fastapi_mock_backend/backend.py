from fastapi import Request
from pydantic import BaseModel, Field, ValidationError, model_validator

from stat_fastapi.exceptions import ConstraintsException
from stat_fastapi.models.opportunity import Opportunity, OpportunitySearch
from stat_fastapi.models.product import Product, Provider, ProviderRole
from stat_fastapi_mock_backend.models import (
    ValidatedOpportunitySearch,
)
from stat_fastapi_mock_backend.satellite import EarthObservationSatelliteModel
from stat_fastapi_mock_backend.settings import Settings


class OffNadirRange(BaseModel):
    minimum: float = Field(ge=0.0, le=45)
    maximum: float = Field(ge=0.0, le=45)

    @model_validator(mode="after")
    def validate(self) -> "OffNadirRange":
        diff = self.maximum - self.minimum
        if diff < 5.0:
            raise ValueError("range must be at least 5°")
        return self


class Constraints(BaseModel):
    off_nadir: OffNadirRange = OffNadirRange(minimum=0.0, maximum=30.0)


PRODUCTS = [
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
        constraints=Constraints.model_json_schema(),
        links=[],
    )
]


class StatMockBackend:
    satellite: EarthObservationSatelliteModel

    def __init__(self):
        settings = Settings.load()
        self.satellite = EarthObservationSatelliteModel(settings.satellite)

    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    def product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """
        return next((product for product in PRODUCTS if product.id == product_id), None)

    async def search_opportunities(
        self, search: OpportunitySearch, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.
        """
        # Additional constraints validation according to this backend's constraints
        try:
            validated = ValidatedOpportunitySearch(**search.model_dump(by_alias=True))
        except ValidationError as exc:
            raise ConstraintsException(exc.errors()) from exc

        try:
            alt = validated.geometry.coordinates[2]
        except IndexError:
            alt = 0
        passes = self.satellite.passes(
            start=validated.properties.datetime[0],
            end=validated.properties.datetime[1],
            lon=validated.geometry.coordinates[0],
            lat=validated.geometry.coordinates[1],
            alt=alt,
            off_nadir_range=(
                validated.properties.off_nadir.minimum,
                validated.properties.off_nadir.maximum,
            ),
        )

        opportunities = [
            Opportunity(
                geometry=p.geometry,
                constraints=search.properties,
                properties=p.properties.model_dump(by_alias=True),
            )
            for p in passes
        ]
        return opportunities
