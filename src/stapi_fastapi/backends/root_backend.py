from typing import Protocol

from fastapi import Request

from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product


class RootBackend(Protocol):
    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """

    def orders(self, request: Request) -> list[Order]:
        """
        Return a list of existing orders.
        """

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.

        Backends must raise `stapi_fastapi.backend.exceptions.NotFoundException`
        if not found or access denied.
        """
