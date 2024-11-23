from __future__ import annotations

from typing import Protocol

from fastapi import Request
from returns.result import Result

from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order, OrderRequest
from stapi_fastapi.routers.product_router import ProductRouter


class ProductBackend(Protocol):  # pragma: nocover
    async def search_opportunities(
        self,
        product_router: ProductRouter,
        search: OpportunityRequest,
        request: Request,
    ) -> Result[list[Opportunity], Exception]:
        """
        Search for ordering opportunities for the  given search parameters.

        Backends must validate search constraints and return
        `stapi_fastapi.exceptions.ConstraintsException` if not valid.
        """

    async def create_order(
        self,
        product_router: ProductRouter,
        search: OrderRequest,
        request: Request,
    ) -> Result[Order, Exception]:
        """
        Create a new order.

        Backends must validate order payload and return
        `stapi_fastapi.exceptions.ConstraintsException` if not valid.
        """
