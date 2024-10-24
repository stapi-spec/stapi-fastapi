from typing import Self, Optional
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from stapi_fastapi.backend import StapiBackend
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.exceptions import StapiException, ConstraintsException, NotFoundException
from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
    OpportunityRequest,
)
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product, ProductsCollection
from stapi_fastapi.models.root import RootResponse
from stapi_fastapi.models.shared import HTTPException as HTTPExceptionModel
from stapi_fastapi.models.shared import Link
from stapi_fastapi.products_router import ProductRouter

"""
/products/{component router} # router for each product added to main router
/orders # list all orders
"""
class MainRouter(APIRouter):

    def __init__(
        self: Self,
        backend: StapiBackend,
        name: str = "main",
        openapi_endpoint_name: str = "openapi",
        docs_endpoint_name: str = "swagger_ui_html",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.backend = backend
        self.name = name
        self.openapi_endpoint_name = openapi_endpoint_name
        self.docs_endpoint_name = docs_endpoint_name

        self.product_routers: dict[str, ProductRouter] = {}

        self.add_api_route(
            "/",
            self.root,
            methods=["GET"],
            name=f"{self.name}:root",
            tags=["Root"],
        )

        self.add_api_route(
            "/products",
            self.products,
            methods=["GET","POST"],
            name=f"{self.name}:list-products",
            tags=["Product"],
        )

        self.add_api_route(
            "/orders/{order_id}",
            self.get_order,
            methods=["GET"],
            name=f"{self.name}:get-order",
            tags=["Orders"],
        )

    def root(self, request: Request) -> RootResponse:
        return RootResponse(
            links=[
                Link(
                    href=str(request.url_for(f"{self.name}:root")),
                    rel="self",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(request.url_for(f"{self.name}:list-products")),
                    rel="products",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(request.url_for(self.openapi_endpoint_name)),
                    rel="service-description",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(request.url_for(self.docs_endpoint_name)),
                    rel="service-docs",
                    type="text/html",
                ),
            ]
        )

    def products(self, request: Request) -> ProductsCollection:
        products = self.backend.products(request)
        for product in products:
            product.links.append(
                Link(
                    href=str(
                        request.url_for(
                            f"{self.name}:get-product", product_id=product.id
                        )
                    ),
                    rel="self",
                    type=TYPE_JSON,
                )
            )
        return ProductsCollection(
            products=products,
            links=[
                Link(
                    href=str(request.url_for(f"{self.name}:list-products")),
                    rel="self",
                    type=TYPE_JSON,
                )
            ],
        )

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.
        """
        try:
            order = await self.backend.get_order(order_id, request)
        except NotFoundException as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found") from exc

        order.links.append(Link(href=str(request.url), rel="self", type=TYPE_GEOJSON))

        return JSONResponse(
            jsonable_encoder(order, exclude_unset=True),
            status.HTTP_200_OK,
            media_type=TYPE_GEOJSON,
        )

    def add_product_router(self, product_router: ProductRouter):
        # Give the include a prefix from the product router
        self.include_router(product_router, prefix=f"/products/{product_router.product.id}")
        self.product_routers[product_router.product.id] = product_router
