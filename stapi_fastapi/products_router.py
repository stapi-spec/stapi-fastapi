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

        # TODO: use add_api_route
        self.post("/opportunities", summary="Search Opportunities for the product")(self.search_opportunities)
        self.get("/parameters", summary="Get parameters for the product")(self.get_product_parameters)
        self.post("/order", summary="Create an order for the product")(self.create_order)

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
