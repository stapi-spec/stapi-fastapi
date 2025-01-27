from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal, Self
from uuid import uuid4

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field, model_validator
from returns.maybe import Maybe
from returns.result import Failure, ResultE, Success

from stapi_fastapi.models.conformance import CORE
from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityProperties,
    OpportunityRequest,
)
from stapi_fastapi.models.order import (
    Order,
    OrderCollection,
    OrderParameters,
    OrderPayload,
    OrderProperties,
    OrderSearchParameters,
    OrderStatus,
    OrderStatusCode,
)
from stapi_fastapi.models.product import (
    Product,
    Provider,
    ProviderRole,
)
from stapi_fastapi.routers.product_router import ProductRouter
from stapi_fastapi.routers.root_router import RootRouter


class InMemoryOrderDB:
    _orders: dict[str, Order] = {}
    _statuses: dict[str, list[OrderStatus]] = defaultdict(list)


async def mock_get_orders(request: Request) -> ResultE[OrderCollection]:
    """
    Show all orders.
    """
    return Success(
        OrderCollection(features=list(request.state._orders_db._orders.values()))
    )


async def mock_get_order(order_id: str, request: Request) -> ResultE[Maybe[Order]]:
    """
    Show details for order with `order_id`.
    """

    return Success(Maybe.from_optional(request.state._orders_db._orders.get(order_id)))


async def mock_get_order_statuses(
    order_id: str, request: Request
) -> ResultE[list[OrderStatus]]:
    return Success(request.state._orders_db._statuses[order_id])


async def mock_search_opportunities(
    product_router: ProductRouter,
    search: OpportunityRequest,
    request: Request,
) -> ResultE[list[Opportunity]]:
    try:
        return Success(
            [
                o.model_copy(update=search.model_dump())
                for o in request.state._opportunities
            ]
        )
    except Exception as e:
        return Failure(e)


async def mock_create_order(
    product_router: ProductRouter, payload: OrderPayload, request: Request
) -> ResultE[Order]:
    """
    Create a new order.
    """
    try:
        status = OrderStatus(
            timestamp=datetime.now(timezone.utc),
            status_code=OrderStatusCode.received,
        )
        order = Order(
            id=str(uuid4()),
            geometry=payload.geometry,
            properties=OrderProperties(
                product_id=product_router.product.id,
                created=datetime.now(timezone.utc),
                status=status,
                search_parameters=OrderSearchParameters(
                    geometry=payload.geometry,
                    datetime=payload.datetime,
                    filter=payload.filter,
                ),
                order_parameters=payload.order_parameters.model_dump(),
                opportunity_properties={
                    "datetime": "2024-01-29T12:00:00Z/2024-01-30T12:00:00Z",
                    "off_nadir": 10,
                },
            ),
            links=[],
        )

        request.state._orders_db._orders[order.id] = order
        request.state._orders_db._statuses[order.id].insert(0, status)
        return Success(order)
    except Exception as e:
        return Failure(e)


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

product = Product(
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
root_router.add_product(product)
app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(root_router, prefix="")
