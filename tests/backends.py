from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, ResultE, Success

from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityPayload,
)
from stapi_fastapi.models.order import (
    Order,
    OrderPayload,
    OrderProperties,
    OrderSearchParameters,
    OrderStatus,
    OrderStatusCode,
)
from stapi_fastapi.routers.product_router import ProductRouter


async def mock_get_orders(
    next: str | None, limit: int, request: Request
) -> ResultE[tuple[list[Order], Maybe[str]]]:
    """
    Return orders from backend.  Handle pagination/limit if applicable
    """
    try:
        start = 0
        limit = min(limit, 100)
        order_ids = [*request.state._orders_db._orders.keys()]

        if next:
            start = order_ids.index(next)
        end = start + limit
        ids = order_ids[start:end]
        orders = [request.state._orders_db._orders[order_id] for order_id in ids]

        if end > 0 and end < len(order_ids):
            return Success(
                (orders, Some(request.state._orders_db._orders[order_ids[end]].id))
            )
        return Success((orders, Nothing))
    except Exception as e:
        return Failure(e)


async def mock_get_order(order_id: str, request: Request) -> ResultE[Maybe[Order]]:
    """
    Show details for order with `order_id`.
    """

    return Success(Maybe.from_optional(request.state._orders_db._orders.get(order_id)))


async def mock_get_order_statuses(
    order_id: str, next: str | None, limit: int, request: Request
) -> ResultE[tuple[list[OrderStatus], Maybe[str]]]:
    try:
        start = 0
        limit = min(limit, 100)
        statuses = request.state._orders_db._statuses[order_id]

        if next:
            start = int(next)
        end = start + limit
        stati = statuses[start:end]

        if end > 0 and end < len(statuses):
            return Success((stati, Some(str(end))))
        return Success((stati, Nothing))
    except Exception as e:
        return Failure(e)


async def mock_search_opportunities(
    product_router: ProductRouter,
    search: OpportunityPayload,
    next: str | None,
    limit: int,
    request: Request,
) -> ResultE[tuple[list[Opportunity], Maybe[str]]]:
    try:
        start = 0
        limit = min(limit, 100)
        if next:
            start = int(next)
        end = start + limit
        opportunities = [
            o.model_copy(update=search.model_dump())
            for o in request.state._opportunities[start:end]
        ]
        if end > 0 and end < len(request.state._opportunities):
            return Success((opportunities, Some(str(end))))
        return Success((opportunities, Nothing))
    except Exception as e:
        return Failure(e)


async def mock_create_order(
    product_router: ProductRouter, payload: OrderPayload, request: Request
) -> ResultE[Order]:
    """
    Create a new order.
    """
    try:
        status = OrderStatus(
            timestamp=datetime.now(timezone.utc),
            status_code=OrderStatusCode.received,
        )
        order = Order(
            id=str(uuid4()),
            geometry=payload.geometry,
            properties=OrderProperties(
                product_id=product_router.product.id,
                created=datetime.now(timezone.utc),
                status=status,
                search_parameters=OrderSearchParameters(
                    geometry=payload.geometry,
                    datetime=payload.datetime,
                    filter=payload.filter,
                ),
                order_parameters=payload.order_parameters.model_dump(),
                opportunity_properties={
                    "datetime": "2024-01-29T12:00:00Z/2024-01-30T12:00:00Z",
                    "off_nadir": 10,
                },
            ),
            links=[],
        )

        request.state._orders_db._orders[order.id] = order
        request.state._orders_db._statuses[order.id].insert(0, status)
        return Success(order)
    except Exception as e:
        return Failure(e)
