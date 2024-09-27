from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from stapi_fastapi.backend import StapiBackend
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.exceptions import ConstraintsException, NotFoundException
from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
    OpportunityRequest,
)
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product, ProductsCollection
from stapi_fastapi.models.root import RootResponse
from stapi_fastapi.models.shared import HTTPException as HTTPExceptionModel
from stapi_fastapi.models.shared import Link


class StapiException(HTTPException):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code, detail)


class StapiRouter:
    NAME_PREFIX = "stapi"
    backend: StapiBackend
    openapi_endpoint_name: str
    docs_endpoint_name: str
    router: APIRouter

    def __init__(
        self,
        backend: StapiBackend,
        openapi_endpoint_name="openapi",
        docs_endpoint_name="swagger_ui_html",
        *args,
        **kwargs,
    ):
        self.backend = backend
        self.openapi_endpoint_name = openapi_endpoint_name
        self.docs_endpoint_name = docs_endpoint_name

        self.router = APIRouter(*args, **kwargs)
        self.router.add_api_route(
            "/",
            self.root,
            methods=["GET"],
            name=f"{self.NAME_PREFIX}:root",
            tags=["Root"],
        )

        self.router.add_api_route(
            "/products",
            self.products,
            methods=["GET"],
            name=f"{self.NAME_PREFIX}:list-products",
            tags=["Product"],
        )
        self.router.add_api_route(
            "/products/{product_id}",
            self.product,
            methods=["GET"],
            name=f"{self.NAME_PREFIX}:get-product",
            tags=["Product"],
            responses={status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionModel}},
        )

        self.router.add_api_route(
            "/opportunities",
            self.search_opportunities,
            methods=["POST"],
            name=f"{self.NAME_PREFIX}:search-opportunities",
            tags=["Opportunities"],
        )

        self.router.add_api_route(
            "/orders",
            self.create_order,
            methods=["POST"],
            name=f"{self.NAME_PREFIX}:create-order",
            tags=["Orders"],
            response_model=Order,
        )
        self.router.add_api_route(
            "/orders/{order_id}",
            self.get_order,
            methods=["GET"],
            name=f"{self.NAME_PREFIX}:get-order",
            tags=["Orders"],
        )

    def root(self, request: Request) -> RootResponse:
        return RootResponse(
            links=[
                Link(
                    href=str(request.url_for(f"{self.NAME_PREFIX}:root")),
                    rel="self",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(request.url_for(f"{self.NAME_PREFIX}:list-products")),
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

        return ProductsCollection(
            products=[
                Product.from_meta(
                    product,
                    links=[
                        Link(
                            href=str(
                                request.url_for(
                                    f"{self.NAME_PREFIX}:get-product",
                                    product_id=product.id,
                                )
                            ),
                            rel="self",
                            type=TYPE_JSON,
                        )
                    ],
                )
                for product in products
            ],
            links=[
                Link(
                    href=str(request.url_for(f"{self.NAME_PREFIX}:list-products")),
                    rel="self",
                    type=TYPE_JSON,
                )
            ],
        )

    def product(self, product_id: str, request: Request) -> Product:
        try:
            product = self.backend.product(product_id, request)
        except NotFoundException as exc:
            raise StapiException(
                status.HTTP_404_NOT_FOUND, "product not found"
            ) from exc

        return Product.from_meta(
            product,
            links=[
                Link(
                    href=str(
                        request.url_for(
                            f"{self.NAME_PREFIX}:get-product", product_id=product.id
                        )
                    ),
                    rel="self",
                    type=TYPE_JSON,
                )
            ],
        )

    async def search_opportunities(
        self, search: OpportunityRequest, request: Request
    ) -> OpportunityCollection:
        """
        Explore the opportunities available for a particular set of constraints
        """
        try:
            opportunities = await self.backend.search_opportunities(search, request)
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)
        return JSONResponse(
            jsonable_encoder(OpportunityCollection(features=opportunities)),
            media_type=TYPE_GEOJSON,
        )

    async def create_order(
        self, search: OpportunityRequest, request: Request
    ) -> JSONResponse:
        """
        Create a new order.
        """
        try:
            order = await self.backend.create_order(search, request)
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
