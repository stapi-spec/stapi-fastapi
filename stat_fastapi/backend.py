from typing import Protocol

from fastapi import Request

from stat_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product


class StatApiBackend(Protocol):
    async def get_products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """

    async def get_product(self, product_id: str, request: Request) -> Product | None:
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
        `stat_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """

    async def create_order(self, search: OpportunityRequest, request: Request) -> Order:
        """
        Create a new order.

        Backends must validate order payload and raise
        `stat_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.

        Backends must raise `stat_fastapi.backend.exceptions.NotFoundException`
        if not found or access denied.
        """
