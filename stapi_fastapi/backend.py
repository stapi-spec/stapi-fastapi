from typing import Protocol

from fastapi import Request

from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import ProductMeta


class StapiBackend(Protocol):
    def products(self, request: Request) -> list[ProductMeta]:
        """
        Return a list of supported products.
        """

    def product(self, product_id: str, request: Request) -> ProductMeta | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """

    async def search_opportunities(
        self, search: OpportunityRequest, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.

        Backends must validate search constraints and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """

    async def create_order(self, search: OpportunityRequest, request: Request) -> Order:
        """
        Create a new order.

        Backends must validate order payload and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.

        Backends must raise `stapi_fastapi.backend.exceptions.NotFoundException`
        if not found or access denied.
        """
