from typing import Self

from fastapi import APIRouter, Request
from fastapi.datastructures import URL

from stapi_fastapi.backends.root_backend import RootBackend
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.models.conformance import CORE, Conformance
from stapi_fastapi.models.order import Order, OrderCollection
from stapi_fastapi.models.product import Product, ProductsCollection
from stapi_fastapi.models.root import RootResponse
from stapi_fastapi.models.shared import Link
from stapi_fastapi.responses import GeoJSONResponse
from stapi_fastapi.routers.product_router import ProductRouter


class RootRouter(APIRouter):
    def __init__(
        self,
        backend: RootBackend,
        conformances: list[str] = [CORE],
        name: str = "root",
        openapi_endpoint_name: str = "openapi",
        docs_endpoint_name: str = "swagger_ui_html",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.backend = backend
        self.name = name
        self.conformances = conformances
        self.openapi_endpoint_name = openapi_endpoint_name
        self.docs_endpoint_name = docs_endpoint_name

        # A dict is used to track the product routers so we can ensure
        # idempotentcy in case a product is added multiple times, and also to
        # manage clobbering if multiple products with the same product_id are
        # added.
        self.product_routers: dict[str, ProductRouter] = {}

        self.add_api_route(
            "/",
            self.get_root,
            methods=["GET"],
            name=f"{self.name}:root",
            tags=["Root"],
        )

        self.add_api_route(
            "/conformance",
            self.get_conformance,
            methods=["GET"],
            name=f"{self.name}:conformance",
            tags=["Conformance"],
        )

        self.add_api_route(
            "/products",
            self.get_products,
            methods=["GET"],
            name=f"{self.name}:list-products",
            tags=["Products"],
        )

        self.add_api_route(
            "/orders",
            self.get_orders,
            methods=["GET"],
            name=f"{self.name}:list-orders",
            response_class=GeoJSONResponse,
            tags=["Orders"],
        )

        self.add_api_route(
            "/orders/{order_id}",
            self.get_order,
            methods=["GET"],
            name=f"{self.name}:get-order",
            response_class=GeoJSONResponse,
            tags=["Orders"],
        )

    def get_root(self, request: Request) -> RootResponse:
        return RootResponse(
            id="STAPI API",
            conformsTo=self.conformances,
            links=[
                Link(
                    href=str(request.url_for(f"{self.name}:root")),
                    rel="self",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(request.url_for(f"{self.name}:conformance")),
                    rel="conformance",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(request.url_for(f"{self.name}:list-products")),
                    rel="products",
                    type=TYPE_JSON,
                ),
                Link(
                    href=str(request.url_for(f"{self.name}:list-orders")),
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
            ],
        )

    def get_conformance(self, request: Request) -> Conformance:
        return Conformance(conforms_to=self.conformances)

    def get_products(self, request: Request) -> ProductsCollection:
        return ProductsCollection(
            products=[pr.get_product(request) for pr in self.product_routers.values()],
            links=[
                Link(
                    href=str(request.url_for(f"{self.name}:list-products")),
                    rel="self",
                    type=TYPE_JSON,
                )
            ],
        )

    async def get_orders(self, request: Request) -> OrderCollection:
        orders = await self.backend.get_orders(request)
        for order in orders:
            order.links.append(
                Link(
                    href=str(
                        request.url_for(f"{self.name}:get-order", order_id=order.id)
                    ),
                    rel="self",
                    type=TYPE_JSON,
                )
            )

        return orders

    async def get_order(self: Self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.
        """
        order = await self.backend.get_order(order_id, request)
        order.links.append(Link(href=str(request.url), rel="self", type=TYPE_GEOJSON))
        return order

    def add_product(self: Self, product: Product) -> None:
        # Give the include a prefix from the product router
        product_router = ProductRouter(product, self)
        self.include_router(product_router, prefix=f"/products/{product.id}")
        self.product_routers[product.id] = product_router

    def generate_order_href(self: Self, request: Request, order_id: int | str) -> URL:
        return request.url_for(f"{self.name}:get-order", order_id=order_id)
