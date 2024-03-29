from typing import Protocol

from fastapi import Request

from stat_fastapi.models.opportunity import Opportunity, OpportunitySearch
from stat_fastapi.models.product import Product


class StatApiBackend(Protocol):
    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """

    def product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """

    async def search_opportunities(
        self, search: OpportunitySearch, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.

        Backends must validate search constraints and raise an
        `stat_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
