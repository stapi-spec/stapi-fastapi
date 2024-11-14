from uuid import uuid4

from fastapi import Request

from stapi_fastapi.backends.product_backend import ProductBackend
from stapi_fastapi.backends.root_backend import RootBackend
from stapi_fastapi.exceptions import ConstraintsException, NotFoundException
from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order, OrderCollection, OrderRequest
from stapi_fastapi.routers.product_router import ProductRouter

from .shared import SpotlightOpportunityProperties, SpotlightOrderParameters


class MockOrderDB(dict[int | str, Order]):
    pass


class MockRootBackend(RootBackend):
    def __init__(self, orders: MockOrderDB) -> None:
        self._orders = orders

    async def get_orders(self, request: Request) -> OrderCollection:
        """
        Show all orders.
        """
        return OrderCollection(features=list(self._orders.values()))

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Show details for order with `order_id`.
        """
        try:
            return self._orders[order_id]
        except KeyError:
            raise NotFoundException()


class MockProductBackend(ProductBackend):
    def __init__(self, orders: MockOrderDB) -> None:
        self._opportunities: list[Opportunity] = []
        self._allowed_payloads: list[OrderRequest] = []
        self._orders = orders

    async def search_opportunities(
        self,
        product_router: ProductRouter,
        search: OpportunityRequest,
        request: Request,
    ) -> list[Opportunity]:
        return [o.model_copy(update=search.model_dump()) for o in self._opportunities]

    async def create_order(
        self,
        product_router: ProductRouter,
        payload: OrderRequest,
        request: Request,
    ) -> Order:
        """
        Create a new order.
        """
        if any(allowed == payload for allowed in self._allowed_payloads):
            order = Order[SpotlightOpportunityProperties, SpotlightOrderParameters](
                id=str(uuid4()),
                geometry=payload.geometry,
                properties={
                    "product_id": product_router.product.id,
                    "datetime": payload.datetime,
                    "geometry": payload.geometry,
                    "filter": payload.filter,
                    "order_parameters": payload.order_parameters,
                    "opportunity_properties": {
                        "datetime": "2024-01-29T12:00:00Z/2024-01-30T12:00:00Z",
                        "off_nadir": 10,
                    },
                },
                links=[],
            )
            self._orders[order.id] = order
            return order
        else:
            raise ConstraintsException(
                f"not allowed: payload {payload.model_dump_json()} not in {[p.model_dump_json() for p in self._allowed_payloads]}"
            )
