from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request

from stapi_fastapi.backends.product_backend import ProductBackend
from stapi_fastapi.backends.root_backend import RootBackend
from stapi_fastapi.exceptions import NotFoundException
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
    OrderRequest,
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


class MockOrderDB(dict[int | str, Order]):
    pass


class MockRootBackend(RootBackend):
    def __init__(self, orders: MockOrderDB) -> None:
        self._orders: MockOrderDB = orders

    async def get_orders(self, request: Request) -> OrderCollection:
        """
        Show all orders.
        """
        return OrderCollection(features=list(self._orders.values()))

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Show details for order with `order_id`.
        """
        try:
            return self._orders[order_id]
        except KeyError:
            raise NotFoundException()


class MockProductBackend(ProductBackend):
    def __init__(self, orders: MockOrderDB) -> None:
        self._opportunities: list[Opportunity] = []
        self._allowed_payloads: list[OrderRequest] = []
        self._orders: MockOrderDB = orders

    async def search_opportunities(
        self,
        product_router: ProductRouter,
        search: OpportunityRequest,
        request: Request,
    ) -> list[Opportunity]:
        return [o.model_copy(update=search.model_dump()) for o in self._opportunities]

    async def create_order(
        self, product_router: ProductRouter, payload: OrderRequest, request: Request
    ) -> Order:
        """
        Create a new order.
        """
        order = Order[MyOpportunityProperties, MyOrderParameters](
            id=str(uuid4()),
            geometry=payload.geometry,
            properties={
                "product_id": product_router.product.id,
                "created": datetime.now(timezone.utc),
                "status": OrderStatus(
                    timestamp=datetime.now(timezone.utc),
                    status_code=OrderStatusCode.accepted,
                ),
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

        self._orders[order.id] = order
        return order


class MyOpportunityProperties(OpportunityProperties):
    off_nadir: int


class MyOrderParameters(OrderParameters):
    s3_path: str | None = None


order_db = MockOrderDB()
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
    constraints=MyOpportunityProperties,
    order_parameters=MyOrderParameters,
    backend=product_backend,
)

root_router = RootRouter(root_backend, conformances=[CORE])
root_router.add_product(product)
app: FastAPI = FastAPI()
app.include_router(root_router, prefix="")
