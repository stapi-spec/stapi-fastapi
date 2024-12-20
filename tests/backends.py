from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request
from returns.result import Failure, ResultE, Success

from stapi_fastapi.backends.product_backend import ProductBackend
from stapi_fastapi.exceptions import ConstraintsException
from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityRequest,
)
from stapi_fastapi.models.order import (
    Order,
    OrderPayload,
    OrderStatus,
    OrderStatusCode,
)
from stapi_fastapi.routers.product_router import ProductRouter

from .application import InMemoryOrderDB


class MockProductBackend(ProductBackend):
    def __init__(self, orders: InMemoryOrderDB) -> None:
        self._opportunities: list[Opportunity] = []
        self._allowed_payloads: list[OrderPayload] = []
        self._orders = orders

    async def search_opportunities(
        self,
        product_router: ProductRouter,
        search: OpportunityRequest,
        request: Request,
    ) -> ResultE[list[Opportunity]]:
        return Success(
            [o.model_copy(update=search.model_dump()) for o in self._opportunities]
        )

    async def create_order(
        self,
        product_router: ProductRouter,
        payload: OrderPayload,
        request: Request,
    ) -> ResultE[Order]:
        """
        Create a new order.
        """
        if any(allowed == payload for allowed in self._allowed_payloads):
            order = Order(
                id=str(uuid4()),
                geometry=payload.geometry,  # maybe set to a different value by opportunity resolution process
                properties={
                    "product_id": product_router.product.id,
                    "created": datetime.now(timezone.utc),
                    "status": OrderStatus(
                        timestamp=datetime.now(timezone.utc),
                        status_code=OrderStatusCode.accepted,
                    ),
                    "search_parameters": {
                        "geometry": payload.geometry,
                        "datetime": payload.datetime,
                        "filter": payload.filter,
                    },
                    "order_parameters": payload.order_parameters.model_dump(),
                    "opportunity_properties": {
                        "datetime": "2024-01-29T12:00:00Z/2024-01-30T12:00:00Z",
                        "off_nadir": 10,
                    },
                },
                links=[],
            )
            self._orders[order.id] = order
            return Success(order)
        else:
            return Failure(
                ConstraintsException(
                    f"not allowed: payload {payload.model_dump_json()} not in {[p.model_dump_json() for p in self._allowed_payloads]}"
                )
            )
