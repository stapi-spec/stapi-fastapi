from fastapi import Request
from pydantic import BaseModel, Field, model_validator

from stat_fastapi.models.opportunity import Opportunity, OpportunitySearch
from stat_fastapi.models.order import Order, OrderPayload
from stat_fastapi.models.product import Product, Provider, ProviderRole
from stat_fastapi_landsat.settings import Settings


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
        id="landsat:standard",
        description="Landsat backend's standard product",
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


class StatLandsatBackend:
    def __init__(self):
        settings = Settings.load()

    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """

    def product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """

    async def search_opportunities(
        self, search: OpportunitySearch, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.
        """

    async def create_order(self, payload: OrderPayload, request: Request) -> Order:
        """
        Create a new order.
        """

    async def get_order(self, order_id: str, request: Request):
        """
        Show details for order with `order_id`.
        """
