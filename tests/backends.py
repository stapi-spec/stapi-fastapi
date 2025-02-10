from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, ResultE, Success

from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityCollection,
    OpportunityPayload,
    OpportunitySearchRecord,
    OpportunitySearchStatus,
    OpportunitySearchStatusCode,
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
        orders = [request.state._orders_db.get_order(order_id) for order_id in ids]

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
    try:
        return Success(
            Maybe.from_optional(request.state._orders_db.get_order(order_id))
        )
    except Exception as e:
        return Failure(e)


async def mock_get_order_statuses(
    order_id: str, next: str | None, limit: int, request: Request
) -> ResultE[Maybe[tuple[list[OrderStatus], Maybe[str]]]]:
    try:
        start = 0
        limit = min(limit, 100)
        statuses = request.state._orders_db.get_order_statuses(order_id)
        if statuses is None:
            return Success(Nothing)

        if next:
            start = int(next)
        end = start + limit
        stati = statuses[start:end]

        if end > 0 and end < len(statuses):
            return Success(Some((stati, Some(str(end)))))
        return Success(Some((stati, Nothing)))
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

        request.state._orders_db.put_order(order)
        request.state._orders_db.put_order_status(order.id, status)
        return Success(order)
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


async def mock_search_opportunities_async(
    product_router: ProductRouter,
    search: OpportunityPayload,
    request: Request,
) -> ResultE[OpportunitySearchRecord]:
    try:
        received_status = OpportunitySearchStatus(
            timestamp=datetime.now(timezone.utc),
            status_code=OpportunitySearchStatusCode.received,
        )
        search_record = OpportunitySearchRecord(
            id=str(uuid4()),
            product_id=product_router.product.id,
            opportunity_request=search,
            status=received_status,
            links=[],
        )
        request.state._opportunities_db.put_search_record(search_record)
        return Success(search_record)
    except Exception as e:
        return Failure(e)


async def mock_get_opportunity_collection(
    product_router: ProductRouter, opportunity_collection_id: str, request: Request
) -> ResultE[Maybe[OpportunityCollection]]:
    try:
        return Success(
            Maybe.from_optional(
                request.state._opportunities_db.get_opportunity_collection(
                    opportunity_collection_id
                )
            )
        )
    except Exception as e:
        return Failure(e)


async def mock_get_opportunity_search_records(
    next: str | None,
    limit: int,
    request: Request,
) -> ResultE[tuple[list[OpportunitySearchRecord], Maybe[str]]]:
    try:
        start = 0
        limit = min(limit, 100)
        search_records = request.state._opportunities_db.get_search_records()

        if next:
            start = int(next)
        end = start + limit
        page = search_records[start:end]

        if end > 0 and end < len(search_records):
            return Success((page, Some(str(end))))
        return Success((page, Nothing))
    except Exception as e:
        return Failure(e)


async def mock_get_opportunity_search_record(
    search_record_id: str, request: Request
) -> ResultE[Maybe[OpportunitySearchRecord]]:
    try:
        return Success(
            Maybe.from_optional(
                request.state._opportunities_db.get_search_record(search_record_id)
            )
        )
    except Exception as e:
        return Failure(e)
