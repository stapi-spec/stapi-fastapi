from typing import Protocol

from fastapi import Request
from returns.maybe import Maybe
from returns.result import ResultE

from stapi_fastapi.models.order import (
    Order,
    Orders,
    OrderStatus,
    OrderStatusPayload,
)


class RootBackend[T: OrderStatusPayload, U: OrderStatus](Protocol):  # pragma: nocover
    async def get_orders(
        self, request: Request, next_token: str, limit: int
    ) -> ResultE[Orders]:
        """
        Return a list of existing orders.
        """
        ...

    async def get_order(self, order_id: str, request: Request) -> ResultE[Maybe[Order]]:
        """
        Get details for order with `order_id`.

        Should return returns.results.Success[Order] if order is found.

        Should return returns.results.Failure[returns.maybe.Nothing] if the order is
        not found or if access is denied.

        A Failure[Exception] will result in a 500.
        """
        ...

    async def get_order_statuses(
        self, order_id: str, request: Request
    ) -> ResultE[list[U]]:
        """
        Get statuses for order with `order_id`.

        Should return returns.results.Success[list[OrderStatus]] if order is found.

        Should return returns.results.Failure[Exception] if the order is
        not found or if access is denied.

        A Failure[Exception] will result in a 500.
        """
        ...

    async def set_order_status(
        self, order_id: str, payload: T, request: Request
    ) -> ResultE[U]:
        """
        Set statuses for order with `order_id`.

        Should return returns.results.Success[OrderStatus] if successful.

        Should return returns.results.Failure[Exception] if the status was not able to be set.

        A Failure[Exception] will result in a 500.
        """
        ...
