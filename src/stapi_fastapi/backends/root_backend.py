from collections.abc import Coroutine
from typing import Any, Callable, TypeVar

from fastapi import Request
from returns.maybe import Maybe
from returns.result import ResultE

from stapi_fastapi.models.opportunity import OpportunitySearchRecord
from stapi_fastapi.models.order import (
    Order,
    OrderStatus,
)

GetOrders = Callable[
    [str | None, int, Request],
    Coroutine[Any, Any, ResultE[tuple[list[Order], Maybe[str]]]],
]
"""
Type alias for an async function that returns a list of existing Orders.

Args:
    next (str | None): A pagination token.
    limit (int): The maximum number of orders to return in a page.
    request (Request): FastAPI's Request object.

Returns:
    A tuple containing a list of orders and a pagination token.

    - Should return returns.result.Success[tuple[list[Order], returns.maybe.Some[str]]] if including a pagination token
    - Should return returns.result.Success[tuple[list[Order], returns.maybe.Nothing]] if not including a pagination token
    - Returning returns.result.Failure[Exception] will result in a 500.
"""

GetOrder = Callable[[str, Request], Coroutine[Any, Any, ResultE[Maybe[Order]]]]
"""
Type alias for an async function that gets details for the order with `order_id`.

Args:
    order_id (str): The order ID.
    request (Request): FastAPI's Request object.

Returns:
    - Should return returns.result.Success[returns.maybe.Some[Order]] if order is found.
    - Should return returns.result.Success[returns.maybe.Nothing] if the order is not found or if access is denied.
    - Returning returns.result.Failure[Exception] will result in a 500.
"""


T = TypeVar("T", bound=OrderStatus)


GetOrderStatuses = Callable[
    [str, str | None, int, Request],
    Coroutine[Any, Any, ResultE[Maybe[tuple[list[T], Maybe[str]]]]],
]
"""
Type alias for an async function that gets statuses for the order with `order_id`.

Args:
    order_id (str): The order ID.
    next (str | None): A pagination token.
    limit (int): The maximum number of statuses to return in a page.
    request (Request): FastAPI's Request object.

Returns:
    A tuple containing a list of order statuses and a pagination token.

    - Should return returns.result.Success[returns.maybe.Some[tuple[list[OrderStatus], returns.maybe.Some[str]]] if order is found and including a pagination token.
    - Should return returns.result.Success[returns.maybe.Some[tuple[list[OrderStatus], returns.maybe.Nothing]]] if order is found and not including a pagination token.
    - Should return returns.result.Success[returns.maybe.Nothing] if the order is not found or if access is denied.
    - Returning returns.result.Failure[Exception] will result in a 500.
"""

GetOpportunitySearchRecords = Callable[
    [str | None, int, Request],
    Coroutine[Any, Any, ResultE[tuple[list[OpportunitySearchRecord], Maybe[str]]]],
]
"""
Type alias for an async function that gets OpportunitySearchRecords for all products.

Args:
    request (Request): FastAPI's Request object.
    next (str | None): A pagination token.
    limit (int): The maximum number of search records to return in a page.

Returns:
    - Should return returns.result.Success[tuple[list[OpportunitySearchRecord], returns.maybe.Some[str]]] if including a pagination token
    - Should return returns.result.Success[tuple[list[OpportunitySearchRecord], returns.maybe.Nothing]] if not including a pagination token
    - Returning returns.result.Failure[Exception] will result in a 500.
"""

GetOpportunitySearchRecord = Callable[
    [str, Request], Coroutine[Any, Any, ResultE[Maybe[OpportunitySearchRecord]]]
]
"""
Type alias for an async function that gets the OpportunitySearchRecord with
`search_record_id`.

Args:
    search_record_id (str): The ID of the OpportunitySearchRecord.
    request (Request): FastAPI's Request object.

Returns:
    - Should return returns.result.Success[returns.maybe.Some[OpportunitySearchRecord]] if the search record is found.
    - Should return returns.result.Success[returns.maybe.Nothing] if the search record is not found or if access is denied.
    - Returning returns.result.Failure[Exception] will result in a 500.
"""
