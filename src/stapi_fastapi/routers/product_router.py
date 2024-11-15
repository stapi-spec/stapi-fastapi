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
from stapi_fastapi.models.order import Order, OrderRequest
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
            # unknown why mypy can't see the constraints property on Product, ignoring
            response_model=OpportunityCollection[Geometry, self.product.constraints],  # type: ignore
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
            path="/order-parameters",
            endpoint=self.get_product_order_parameters,
            name=f"{self.root_router.name}:{self.product.id}:get-order-parameters",
            methods=["GET"],
            summary="Get order parameters for the product",
            tags=["Products"],
        )

        # This wraps `self.create_order` to explicitly parameterize `OrderRequest`
        # for this Product. This must be done programmatically instead of with a type
        # annotation because it's setting the type dynamically instead of statically, and
        # pydantic needs this type annotation when doing object conversion. This cannot be done
        # directly to `self.create_order` because doing it there changes
        # the annotation on every `ProductRouter` instance's `create_order`, not just
        # this one's.
        async def _create_order(
            payload: OrderRequest,
            request: Request,
            response: Response,
        ) -> Order:
            return await self.create_order(payload, request, response)

        _create_order.__annotations__["payload"] = OrderRequest[
            self.product.order_parameters  # type: ignore
        ]

        self.add_api_route(
            path="/order",
            endpoint=_create_order,
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
                Link(
                    href=str(
                        request.url_for(
                            f"{self.root_router.name}:{self.product.id}:get-constraints",
                        ),
                    ),
                    rel="constraints",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(
                        request.url_for(
                            f"{self.root_router.name}:{self.product.id}:get-order-parameters",
                        ),
                    ),
                    rel="order-parameters",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(
                        request.url_for(
                            f"{self.root_router.name}:{self.product.id}:search-opportunities",
                        ),
                    ),
                    rel="opportunities",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(
                        request.url_for(
                            f"{self.root_router.name}:{self.product.id}:create-order",
                        ),
                    ),
                    rel="create-order",
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

        return OpportunityCollection(
            features=opportunities,
            links=[
                Link(
                    href=str(
                        request.url_for(
                            f"{self.root_router.name}:{self.product.id}:create-order",
                        ),
                    ),
                    rel="create-order",
                    type=TYPE_JSON,
                ),
            ],
        )

    def get_product_constraints(self: Self) -> JsonSchemaModel:
        """
        Return supported constraints of a specific product
        """
        return self.product.constraints

    def get_product_order_parameters(self: Self) -> JsonSchemaModel:
        """
        Return supported constraints of a specific product
        """
        return self.product.order_parameters

    async def create_order(
        self, payload: OrderRequest, request: Request, response: Response
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
