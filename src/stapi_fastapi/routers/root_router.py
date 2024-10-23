from typing import Self

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from stapi_fastapi.backends.root_backend import RootBackend
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.exceptions import NotFoundException
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product, ProductsCollection
from stapi_fastapi.models.root import RootResponse
from stapi_fastapi.models.shared import Link
from stapi_fastapi.routers.product_router import ProductRouter


class RootRouter(APIRouter):
    def __init__(
        self: Self,
        backend: RootBackend,
        name: str = "root",
        openapi_endpoint_name="openapi",
        docs_endpoint_name="swagger_ui_html",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.backend = backend
        self.name = name
        self.openapi_endpoint_name = openapi_endpoint_name
        self.docs_endpoint_name = docs_endpoint_name

        self.product_routers: dict[str, ProductRouter] = {}

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
            "/orders",
            self.orders,
            methods=["GET"],
            name=f"{self.NAME_PREFIX}:list-orders",
            tags=["Order"],
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
                    href=str(request.url_for(f"{self.NAME_PREFIX}:list-orders")),
                    rel="orders",
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
        products: list[Product] = []
        for product_router in self.product_routers:
            product = product_router.product
            products.append(product)
            product.links.append(
                Link(
                    href=str(
                        request.url_for(
                            f"{self.NAME_PREFIX}:get-product", product_id=product.id
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
                    href=str(request.url_for(f"{self.NAME_PREFIX}:list-products")),
                    rel="self",
                    type=TYPE_JSON,
                )
            ],
        )

    def orders(self, request: Request) -> list[Order]:
        orders = self.backend.orders(request)
        for order in orders:
            order.links.append(
                Link(
                    href=str(
                        request.url_for(
                            f"{self.NAME_PREFIX}:get-order", order_id=order.id
                        )
                    ),
                    rel="self",
                    type=TYPE_JSON,
                )
            )
        return list[Order]

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
        self.include_router(
            product_router, prefix=f"/products/{product_router.product.id}"
        )
        self.product_routers[product_router.product.id] = product_router
