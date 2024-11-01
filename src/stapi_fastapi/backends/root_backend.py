from typing import Protocol

from fastapi import Request

from stapi_fastapi.models.order import Order, OrderCollection


class RootBackend(Protocol):  # pragma: nocover
    async def get_orders(self, request: Request) -> OrderCollection:
        """
        Return a list of existing orders.
        """
        ...

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.

        Backends must raise `stapi_fastapi.exceptions.NotFoundException`
        if not found or access denied.
        """
        ...
