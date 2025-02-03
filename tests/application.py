from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Literal, Self

from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

from stapi_fastapi.models.conformance import CORE
from stapi_fastapi.models.opportunity import (
    OpportunityProperties,
)
from stapi_fastapi.models.order import (
    Order,
    OrderParameters,
    OrderStatus,
)
from stapi_fastapi.models.product import (
    Product,
    Provider,
    ProviderRole,
)
from stapi_fastapi.routers.root_router import RootRouter

from .backends import (
    mock_create_order,
    mock_get_order,
    mock_get_order_statuses,
    mock_get_orders,
    mock_search_opportunities,
)


class InMemoryOrderDB:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._statuses: dict[str, list[OrderStatus]] = defaultdict(list)


class MyProductConstraints(BaseModel):
    off_nadir: int


class OffNadirRange(BaseModel):
    minimum: int = Field(ge=0, le=45)
    maximum: int = Field(ge=0, le=45)

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("range minimum cannot be greater than maximum")
        return self


class MyOpportunityProperties(OpportunityProperties):
    off_nadir: OffNadirRange
    vehicle_id: list[Literal[1, 2, 5, 7, 8]]
    platform: Literal["platform_id"]


class MyOrderParameters(OrderParameters):
    s3_path: str | None = None


provider = Provider(
    name="Test Provider",
    description="A provider for Test data",
    roles=[ProviderRole.producer],  # Example role
    url="https://test-provider.example.com",  # Must be a valid URL
)

mock_product_test_spotlight = Product(
    id="test-spotlight",
    title="Test Spotlight Product",
    description="Test product for test spotlight",
    license="CC-BY-4.0",
    keywords=["test", "satellite"],
    providers=[provider],
    links=[],
    create_order=mock_create_order,
    search_opportunities=mock_search_opportunities,
    constraints=MyProductConstraints,
    opportunity_properties=MyOpportunityProperties,
    order_parameters=MyOrderParameters,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    try:
        yield {
            "_orders_db": InMemoryOrderDB(),
        }
    finally:
        pass


root_router = RootRouter(
    get_orders=mock_get_orders,
    get_order=mock_get_order,
    get_order_statuses=mock_get_order_statuses,
    conformances=[CORE],
)
root_router.add_product(mock_product_test_spotlight)
app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(root_router, prefix="")
