from typing import Protocol

from fastapi import Request
from returns.maybe import Maybe
from returns.result import ResultE

from stapi_fastapi.models.order import (
    Order,
    OrderStatus,
)


class RootBackend[T: OrderStatus](Protocol):  # pragma: nocover
    async def get_orders(
        self, request: Request, next: str | None, limit: int
    ) -> ResultE[tuple[list[Order], Maybe[str]]]:
        """
        Return a list of existing orders and pagination token if applicable
        No pagination will return empty string for token
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
        self, order_id: str, request: Request, next: str | None, limit: int
    ) -> ResultE[tuple[list[T], Maybe[str]]]:
        """
        Get statuses for order with `order_id`.

        Should return returns.results.Success[list[OrderStatus]] if order is found.

        Should return returns.results.Failure[Exception] if the order is
        not found or if access is denied.

        A Failure[Exception] will result in a 500.
        """
        ...
