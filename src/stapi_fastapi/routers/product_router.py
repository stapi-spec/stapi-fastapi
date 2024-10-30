# Generic product router factory
from __future__ import annotations

from typing import Self

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import stapi_fastapi
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
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
        root_router: stapi_fastapi.routers.RootRouter,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.product = product
        self.root_router = root_router

        self.add_api_route(
            path="",
            endpoint=self.get_product,
            name=f"{self.root_router.name}:{self.product.id}:get-product",
            methods=["GET"],
            summary="Retrieve this product",
        )

        self.add_api_route(
            path="/opportunities",
            endpoint=self.search_opportunities,
            name=f"{self.root_router.name}:{self.product.id}:search-opportunities",
            methods=["POST"],
            summary="Search Opportunities for the product",
        )

        self.add_api_route(
            path="/constraints",
            endpoint=self.get_product_constraints,
            name=f"{self.root_router.name}:{self.product.id}:get-constraints",
            methods=["GET"],
            summary="Get constraints for the product",
        )

        self.add_api_route(
            path="/order",
            endpoint=self.create_order,
            name=f"{self.root_router.name}:{self.product.id}:create-order",
            methods=["POST"],
            summary="Create an order for the product",
        )

    def get_product(self, request: Request) -> Product:
        return self.product.with_links(
            links=[
                Link(
                    href=str(
                        request.url_for(
                            f"{self.root_router.name}:{self.product.id}:get-product",
                        ),
                    ),
                    rel="self",
                    type=TYPE_JSON,
                ),
            ],
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
            "product.id": self.product.product.id,
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

        location = self.root_router.generate_order_href(request, order.id)
        order.links.append(Link(href=location, rel="self", type=TYPE_GEOJSON))
        return JSONResponse(
            jsonable_encoder(order, exclude_unset=True),
            status.HTTP_201_CREATED,
            {"Location": location},
            TYPE_GEOJSON,
        )
