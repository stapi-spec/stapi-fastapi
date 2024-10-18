# Generic product router factory
from typing import Self
from fastapi import APIRouter, HTTPException, status, Request
from stapi_fastapi.models.opportunity import OpportunityRequest
from stapi_fastapi.models.product import Product
from stapi_fastapi.backend import StapiBackend
from stapi_fastapi.exceptions import ConstraintsException

"""
/products[MainRouter]/opportunities
/products[MainRouter]/parameters
/products[MainRouter]/order
"""

class ProductRouter(APIRouter):

    def __init__(
        self: Self,
        product: Product,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.product = product

        self.add_api_route(
            path="/opportunities",
            endpoint=self.search_opportunities,
            methods=["POST"],
            summary="Search Opportunities for the product"
        )

        self.add_api_route(
            path="/parameters",
            endpoint=self.get_product_parameters,
            methods=["GET"],
            summary="Get parameters for the product"
        )

        self.add_api_route(
            path="/order",
            endpoint=self.create_order,
            methods=["POST"],
            summary="Create an order for the product"
        )

    async def search_opportunities(self: Self, request: Request, search: OpportunityRequest):
        try:
            opportunities = await self.product.search_opportunities(search, request)
            return opportunities
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)

    async def get_product_parameters(self: Self, request: Request):
        return {"product_id": self.product.id, "parameters": self.product.parameters}

    async def create_order(self: Self, request: Request, payload: OpportunityRequest):
        try:
            order = await self.product.create_order(payload, request)
            return order
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)
