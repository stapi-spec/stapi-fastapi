# Generic product router factory
from typing import Self

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from stapi_fastapi.constants import TYPE_GEOJSON
from stapi_fastapi.exceptions import ConstraintsException
from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
    OpportunityRequest,
)
from stapi_fastapi.models.product import Product
from stapi_fastapi.models.shared import Link
from stapi_fastapi.types.json_schema_model import JsonSchemaModel

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
            summary="Search Opportunities for the product",
        )

        self.add_api_route(
            path="/constraints",
            endpoint=self.get_product_constraints,
            methods=["GET"],
            summary="Get constraints for the product",
        )

        self.add_api_route(
            path="/order",
            endpoint=self.create_order,
            methods=["POST"],
            summary="Create an order for the product",
        )

    async def search_opportunities(
        self, search: OpportunityRequest, request: Request
    ) -> OpportunityCollection:
        """
        Explore the opportunities available for a particular set of constraints
        """
        try:
            opportunities = await self.product.backend.search_opportunities(
                search, request
            )
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)
        return JSONResponse(
            jsonable_encoder(OpportunityCollection(features=opportunities)),
            media_type=TYPE_GEOJSON,
        )

    async def get_product_constraints(self: Self, request: Request) -> JsonSchemaModel:
        """
        Return supported constraints of a specific product
        """
        return {
            "product_id": self.product.product_id,
            "constraints": self.product.constraints,
        }

    async def create_order(
        self, payload: OpportunityRequest, request: Request
    ) -> JSONResponse:
        """
        Create a new order.
        """
        try:
            order = await self.product.backend.create_order(payload, request)
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)

        location = str(
            request.url_for(f"{self.NAME_PREFIX}:get-order", order_id=order.id)
        )
        order.links.append(Link(href=location, rel="self", type=TYPE_GEOJSON))
        return JSONResponse(
            jsonable_encoder(order, exclude_unset=True),
            status.HTTP_201_CREATED,
            {"Location": location},
            TYPE_GEOJSON,
        )
