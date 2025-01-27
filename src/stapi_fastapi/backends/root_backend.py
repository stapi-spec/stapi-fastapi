from typing import Any, Callable, Coroutine, TypeVar

from fastapi import Request
from returns.maybe import Maybe
from returns.result import ResultE

from stapi_fastapi.models.order import (
    Order,
    OrderCollection,
    OrderStatus,
)

GetOrders = Callable[[Request], Coroutine[Any, Any, ResultE[OrderCollection]]]
"""
Type alias for an async function that returns a list of existing Orders.

Args:
    request (Request): FastAPI's Request object.

Returns:
    - Should return returns.result.Success[OrderCollection]
    - Returning returns.result.Failure[Exception] will result in a 500.
"""

GetOrder = Callable[[str, Request], Coroutine[Any, Any, ResultE[Maybe[Order]]]]
"""
Type alias for an async function that gets details for the order with `order_id`.

Args:
    order_id (str): The order ID.
    request (Request): FastAPI's Request object.

Returns:
    - Should return returns.result.Success[Order] if order is found.
    - Should return returns.result.Failure[returns.maybe.Nothing] if the order is not
    found or if access is denied.
    - Returning returns.result.Failure[Exception] will result in a 500.
"""


T = TypeVar("T", bound=OrderStatus)


GetOrderStatuses = Callable[[str, Request], Coroutine[Any, Any, ResultE[list[T]]]]
"""
Type alias for an async function that gets statuses for the order with `order_id`.

Args:
    order_id (str): The order ID.
    request (Request): FastAPI's Request object.

Returns:
    - Should return returns.result.Success[list[OrderStatus]] if order is found.
    - Should return returns.result.Failure[Exception] if the order is not found or if
    access is denied.
    - Returning returns.result.Failure[Exception] will result in a 500.
"""
