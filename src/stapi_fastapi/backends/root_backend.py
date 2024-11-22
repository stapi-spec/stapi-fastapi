from typing import Protocol

from fastapi import Request
from returns.maybe import Maybe
from returns.result import Result

from stapi_fastapi.models.order import Order, OrderCollection


class RootBackend(Protocol):  # pragma: nocover
    async def get_orders(self, request: Request) -> Result[OrderCollection, Exception]:
        """
        Return a list of existing orders.
        """
        ...

    async def get_order(
        self, order_id: str, request: Request
    ) -> Result[Maybe[Order], Exception]:
        """
        Get details for order with `order_id`.

        Should return returns.results.Success[Order] if order is found.

        Should return returns.results.Failure[returns.maybe.Nothing] if the order is
        not found or if access is denied. If there is an Exception associated with attempting to find the order,
        then resturns.results.Failure[returns.maybe.Some[Exception]] should be returned.

        Typically, a Failure[Nothing] will result in a 404 and Failure[Some[Exception]] will resulting in a 500.
        """
        ...
