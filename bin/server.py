from uuid import uuid4

from fastapi import FastAPI, Request
from stapi_fastapi.backends.product_backend import ProductBackend
from stapi_fastapi.exceptions import ConstraintsException, NotFoundException
from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityPropertiesBase,
    OpportunityRequest,
)
from stapi_fastapi.models.order import Order, OrderParametersBase, OrderRequest
from stapi_fastapi.models.product import (
    Product,
    Provider,
    ProviderRole,
)
from stapi_fastapi.routers.product_router import ProductRouter
from stapi_fastapi.routers.root_router import RootRouter


class MockOrderDB(dict[int | str, Order]):
    pass


class MockRootBackend:
    def __init__(self, orders: MockOrderDB) -> None:
        self._orders: MockOrderDB = orders

    async def get_orders(self, request: Request) -> list[Order]:
        """
        Show all orders.
        """
        return list(self._orders.values())

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
        allowed: bool = any(allowed == payload for allowed in self._allowed_payloads)
        allowed = True
        if allowed:
            order = Order(
                id=str(uuid4()),
                geometry=payload.geometry,
                properties={
                    "filter": payload.filter,
                    "datetime": payload.datetime,
                    "product_id": product_router.product.id,
                    **dict(payload.order_parameters),
                },
                links=[],
            )
            self._orders[order.id] = order
            return order
        raise ConstraintsException("not allowed")


class TestSpotlightProperties(OpportunityPropertiesBase):
    off_nadir: int


class TestOrderParameters(OrderParametersBase):
    s3_path: str


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
    order_parameters=TestOrderParameters,
    backend=product_backend,
)

root_router = RootRouter(root_backend)
root_router.add_product(product)
app: FastAPI = FastAPI()
app.include_router(root_router, prefix="")
