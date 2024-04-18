"""Umbra Backend Module"""

from typing import Protocol

from fastapi import HTTPException, Request

from stat_fastapi.models.opportunity import Opportunity, OpportunitySearch
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product
from stat_fastapi_umbra_backend.products import PRODUCTS


class UmbraBackend(Protocol):
    """Umbra STAT Backend"""

    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    def product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """
        filtered_products = [p for p in PRODUCTS if p.id == product_id]
        if filtered_products:
            return filtered_products[0]
        raise HTTPException(status_code=404, detail="Product not found")

    async def search_opportunities(
        self, search: OpportunitySearch, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.

        Backends must validate search constraints and raise
        `stat_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """

    async def create_order(self, search: OpportunitySearch, request: Request) -> Order:
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
