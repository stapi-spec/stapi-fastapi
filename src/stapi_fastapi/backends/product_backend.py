from __future__ import annotations

from typing import Any, Callable, Coroutine

from fastapi import Request
from returns.maybe import Maybe
from returns.result import ResultE

from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order, OrderPayload
from stapi_fastapi.routers.product_router import ProductRouter

SearchOpportunities = Callable[
    [ProductRouter, OpportunityRequest, Request, str | None, int],
    Coroutine[Any, Any, ResultE[tuple[list[Opportunity], Maybe[str]]]],
]
"""
Type alias for an async function that searches for ordering opportunities for the given
search parameters.

Args:
    product_router (ProductRouter): The product router.
    search (OpportunityRequest): The search parameters.
    request (Request): FastAPI's Request object.
    next (str | None): A pagination token.
    limit (int): The maximum number of opportunities to return in a page.

Returns:
    A tuple containing a list of opportunities and a pagination token.

    - Should return returns.result.Success[tuple[list[Opportunity], returns.maybe.Some[str]]] if including a pagination token
    - Should return returns.result.Success[tuple[list[Opportunity], returns.maybe.Nothing]] if not including a pagination token
    - Returning returns.result.Failure[Exception] will result in a 500.

Note:
    Backends must validate search constraints and return
    returns.result.Failure[stapi_fastapi.exceptions.ConstraintsException] if not valid.
"""

CreateOrder = Callable[
    [ProductRouter, OrderPayload, Request], Coroutine[Any, Any, ResultE[Order]]
]
"""
Type alias for an async function that creates a new order.

Args:
    product_router (ProductRouter): The product router.
    payload (OrderPayload): The order payload.
    request (Request): FastAPI's Request object.

Returns:
    - Should return returns.result.Success[Order]
    - Returning returns.result.Failure[Exception] will result in a 500.

Note:
    Backends must validate order payload and return
    returns.result.Failure[stapi_fastapi.exceptions.ConstraintsException] if not valid.
"""
