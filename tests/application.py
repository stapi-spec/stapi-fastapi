from collections import defaultdict
from datetime import datetime, timezone
from typing import Literal, Self
from uuid import uuid4

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field, model_validator
from returns.maybe import Maybe
from returns.result import Failure, ResultE, Success

from stapi_fastapi.backends.product_backend import ProductBackend
from stapi_fastapi.backends.root_backend import RootBackend
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
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._statuses: dict[str, list[OrderStatus]] = defaultdict(list)


class MockRootBackend(RootBackend):
    def __init__(self, orders: InMemoryOrderDB) -> None:
        self._orders_db: InMemoryOrderDB = orders

    async def get_orders(
        self, request: Request, next: str | None, limit: int
    ) -> ResultE[tuple[OrderCollection, str]]:
        """
        Return orders from backend.  Handle pagination/limit if applicable
        """
        try:
            start = 0
            if limit > 100:
                limit = 100

            order_ids = [*self._orders_db._orders.keys()]

            if next:
                start = order_ids.index(next)
            if not order_ids and not next:  # no data in db
                return Success((OrderCollection(features=[]), ""))

            end = start + limit
            ids = order_ids[start:end]
            feats = [self._orders_db._orders[order_id] for order_id in ids]

            next = ""
            if end < len(order_ids):
                next = self._orders_db._orders[order_ids[end]].id
            return Success((OrderCollection(features=feats), next))
        except Exception as e:
            return Failure(e)

    async def get_order(self, order_id: str, request: Request) -> ResultE[Maybe[Order]]:
        """
        Show details for order with `order_id`.
        """

        return Success(Maybe.from_optional(self._orders_db._orders.get(order_id)))

    async def get_order_statuses(
        self, order_id: str, request: Request
    ) -> ResultE[list[OrderStatus]]:
        return Success(self._orders_db._statuses[order_id])


class MockProductBackend(ProductBackend):
    def __init__(self, orders: InMemoryOrderDB) -> None:
        self._opportunities: list[Opportunity] = []
        self._allowed_payloads: list[OrderPayload] = []
        self._orders_db: InMemoryOrderDB = orders

    async def search_opportunities(
        self,
        product_router: ProductRouter,
        search: OpportunityRequest,
        request: Request,
    ) -> ResultE[list[Opportunity]]:
        try:
            return Success(
                [o.model_copy(update=search.model_dump()) for o in self._opportunities]
            )
        except Exception as e:
            return Failure(e)

    async def create_order(
        self, product_router: ProductRouter, payload: OrderPayload, request: Request
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
                properties={
                    "product_id": product_router.product.id,
                    "created": datetime.now(timezone.utc),
                    "status": status,
                    "search_parameters": {
                        "geometry": payload.geometry,
                        "datetime": payload.datetime,
                        "filter": payload.filter,
                    },
                    "order_parameters": payload.order_parameters.model_dump(),
                    "opportunity_properties": {
                        "datetime": "2024-01-29T12:00:00Z/2024-01-30T12:00:00Z",
                        "off_nadir": 10,
                    },
                },
                links=[],
            )

            self._orders_db._orders[order.id] = order
            self._orders_db._statuses[order.id].insert(0, status)
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


order_db = InMemoryOrderDB()
product_backend = MockProductBackend(order_db)
root_backend = MockRootBackend(order_db)

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
    constraints=MyProductConstraints,
    opportunity_properties=MyOpportunityProperties,
    order_parameters=MyOrderParameters,
    backend=product_backend,
)

root_router = RootRouter(root_backend, conformances=[CORE])
root_router.add_product(product)
app: FastAPI = FastAPI()
app.include_router(root_router, prefix="")
