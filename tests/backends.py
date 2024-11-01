from uuid import uuid4

from fastapi import Request
from stapi_fastapi.backends.product_backend import ProductBackend
from stapi_fastapi.exceptions import ConstraintsException, NotFoundException
from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product


class MockOrderDB(dict[int | str, Order]):
    pass


class MockRootBackend:
    def __init__(self, orders: MockOrderDB) -> None:
        self._orders = orders

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
        self._allowed_payloads: list[OpportunityRequest] = []
        self._orders = orders

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
        allowed = any(allowed == payload for allowed in self._allowed_payloads)
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