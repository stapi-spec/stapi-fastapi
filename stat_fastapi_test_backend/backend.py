from typing import Mapping
from uuid import uuid4

from fastapi import Request

from stat_fastapi.exceptions import ConstraintsException, NotFoundException
from stat_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product


class TestBackend:
    _products: list[Product] = []
    _opportunities: list[Opportunity] = []
    _allowed_payloads: list[OpportunityRequest] = []
    _orders: Mapping[str, Order] = {}

    async def get_products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return self._products

    async def get_product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """
        try:
            return next(
                (product for product in self._products if product.id == product_id)
            )
        except StopIteration as exc:
            raise NotFoundException() from exc

    async def search_opportunities(
        self, search: OpportunityRequest, request: Request
    ) -> list[Opportunity]:
        return [o.model_copy(update=search.model_dump()) for o in self._opportunities]

    async def create_order(
        self, payload: OpportunityRequest, request: Request
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
                    "product_id": payload.product_id,
                },
                links=[],
            )
            self._orders[order.id] = order
            return order
        raise ConstraintsException("not allowed")

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Show details for order with `order_id`.
        """
        try:
            return self._orders[order_id]
        except KeyError:
            raise NotFoundException()
