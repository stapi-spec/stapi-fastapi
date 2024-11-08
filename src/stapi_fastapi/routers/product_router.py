from __future__ import annotations

from typing import TYPE_CHECKING, Self

from fastapi import APIRouter, HTTPException, Request, Response, status
from geojson_pydantic.geometries import Geometry

from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.exceptions import ConstraintsException
from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
    OpportunityRequest,
)
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product
from stapi_fastapi.models.shared import Link
from stapi_fastapi.responses import GeoJSONResponse
from stapi_fastapi.types.json_schema_model import JsonSchemaModel

if TYPE_CHECKING:
    from stapi_fastapi.routers import RootRouter


class ProductRouter(APIRouter):
    def __init__(
        self,
        product: Product,
        root_router: RootRouter,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.product = product
        self.root_router = root_router

        self.add_api_route(
            path="",
            endpoint=self.get_product,
            name=f"{self.root_router.name}:{self.product.id}:get-product",
            methods=["GET"],
            summary="Retrieve this product",
            tags=["Products"],
        )

        self.add_api_route(
            path="/opportunities",
            endpoint=self.search_opportunities,
            name=f"{self.root_router.name}:{self.product.id}:search-opportunities",
            methods=["POST"],
            response_class=GeoJSONResponse,
            response_model=OpportunityCollection[Geometry, self.product.constraints],
            summary="Search Opportunities for the product",
            tags=["Products"],
        )

        self.add_api_route(
            path="/constraints",
            endpoint=self.get_product_constraints,
            name=f"{self.root_router.name}:{self.product.id}:get-constraints",
            methods=["GET"],
            summary="Get constraints for the product",
            tags=["Products"],
        )

        self.add_api_route(
            path="/order",
            endpoint=self.create_order,
            name=f"{self.root_router.name}:{self.product.id}:create-order",
            methods=["POST"],
            response_class=GeoJSONResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create an order for the product",
            tags=["Products"],
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
                self, search, request
            )
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)

        return OpportunityCollection(features=opportunities)

    async def get_product_constraints(self: Self) -> JsonSchemaModel:
        """
        Return supported constraints of a specific product
        """
        return self.product.constraints

    async def create_order(
        self, payload: OpportunityRequest, request: Request, response: Response
    ) -> Order:
        """
        Create a new order.
        """
        try:
            order = await self.product.backend.create_order(
                self,
                payload,
                request,
            )
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)

        location = str(self.root_router.generate_order_href(request, order.id))
        order.links.append(Link(href=location, rel="self", type=TYPE_GEOJSON))
        response.headers["Location"] = location
        return order
