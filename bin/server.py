from uuid import uuid4

from fastapi import FastAPI, Request

from stapi_fastapi.backends.product_backend import ProductBackend
from stapi_fastapi.backends.root_backend import RootBackend
from stapi_fastapi.exceptions import ConstraintsException, NotFoundException
from stapi_fastapi.models.conformance import CORE
from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityPropertiesBase,
    OpportunityRequest,
)
from stapi_fastapi.models.order import Order, OrderCollection
from stapi_fastapi.models.product import (
    OrderParameters,
    Product,
    Provider,
    ProviderRole,
)
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
        self._allowed_payloads: list[OpportunityRequest] = []
        self._orders: MockOrderDB = orders

    async def search_opportunities(
        self, product: Product, search: OpportunityRequest, request: Request
    ) -> list[Opportunity]:
        return [o.model_copy(update=search.model_dump()) for o in self._opportunities]

    async def create_order(
        self, product: Product, payload: OpportunityRequest, request: Request
    ) -> Order:
        """
        Create a new order.
        """
        allowed: bool = any(allowed == payload for allowed in self._allowed_payloads)
        if allowed:
            order = Order(
                id=str(uuid4()),
                geometry=payload.geometry,
                properties={
                    "filter": payload.filter,
                    "datetime": payload.datetime,
                    "product_id": product.id,
                },
                links=[],
            )
            self._orders[order.id] = order
            return order
        raise ConstraintsException("not allowed")


class TestSpotlightProperties(OpportunityPropertiesBase):
    off_nadir: int


class TestSpotlightOrderParameters(OrderParameters):
    delivery_mechanism: str | None = None


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
    constraints=TestSpotlightProperties,
    order_parameters=TestSpotlightOrderParameters,
    backend=product_backend,
)

root_router = RootRouter(root_backend, conformances=[CORE])
root_router.add_product(product)
app: FastAPI = FastAPI()
app.include_router(root_router, prefix="")
