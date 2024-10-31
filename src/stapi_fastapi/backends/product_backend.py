from __future__ import annotations

from typing import Protocol

from fastapi import Request

import stapi_fastapi
from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order


class ProductBackend(Protocol):
    async def search_opportunities(
        self,
        product: stapi_fastapi.models.product.Product,
        search: OpportunityRequest,
        request: Request,
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.

        Backends must validate search constraints and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        ...

    async def create_order(
        self,
        product: stapi_fastapi.models.product.Product,
        search: OpportunityRequest,
        request: Request,
    ) -> Order:
        """
        Create a new order.

        Backends must validate order payload and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        ...