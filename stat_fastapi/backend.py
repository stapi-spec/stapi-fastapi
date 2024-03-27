from typing import Protocol

from fastapi import Request

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
