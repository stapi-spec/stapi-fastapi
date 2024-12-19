import logging
from typing import Self

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.datastructures import URL
from fastapi.responses import Response
from returns.maybe import Maybe, Some
from returns.result import Failure, Success

from stapi_fastapi.backends.root_backend import RootBackend
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.exceptions import NotFoundException
from stapi_fastapi.models.conformance import CORE, Conformance
from stapi_fastapi.models.order import (
    Order,
    OrderCollection,
    OrderStatuses,
    OrderStatusPayload,
)
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

        self.add_api_route(
            "/orders/{order_id}/statuses",
            self.get_order_statuses,
            methods=["GET"],
            name=f"{self.name}:list-order-statuses",
            tags=["Orders"],
        )

        self.add_api_route(
            "/orders/{order_id}/statuses",
            self.set_order_status,
            methods=["POST"],
            name=f"{self.name}:set-order-status",
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
        match await self.backend.get_orders(request):
            case Success(orders):
                for order in orders:
                    order.links.append(
                        Link(
                            href=str(
                                request.url_for(
                                    f"{self.name}:get-order", order_id=order.id
                                )
                            ),
                            rel="self",
                            type=TYPE_JSON,
                        )
                    )
                return orders
            case Failure(e):
                logging.exception("An error occurred while retrieving orders", e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error finding Orders",
                )
            case _:
                raise AssertionError("Expected code to be unreachable")

    async def get_order(self: Self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.
        """
        match await self.backend.get_order(order_id, request):
            case Success(Some(order)):
                self.add_order_links(order, request)
                return order
            case Success(Maybe.empty):
                raise NotFoundException("Order not found")
            case Failure(e):
                logging.exception(
                    f"An error occurred while retrieving order '{order_id}'", e
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error finding Order",
                )
            case _:
                raise AssertionError("Expected code to be unreachable")

    async def get_order_statuses(
        self: Self, order_id: str, request: Request
    ) -> OrderStatuses:
        match await self.backend.get_order_statuses(order_id, request):
            case Success(statuses):
                return OrderStatuses(
                    statuses=statuses,
                    links=[
                        Link(
                            href=str(
                                request.url_for(
                                    f"{self.name}:list-order-statuses",
                                    order_id=order_id,
                                )
                            ),
                            rel="self",
                            type=TYPE_JSON,
                        )
                    ],
                )
            case Failure(e):
                logging.exception(
                    "An error occurred while retrieving order statuses", e
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error finding Order Statuses",
                )
            case _:
                raise AssertionError("Expected code to be unreachable")

    async def set_order_status(
        self, order_id: str, payload: OrderStatusPayload, request: Request
    ) -> Response:
        match await self.backend.set_order_status(order_id, payload, request):
            case Success(_):
                return Response(status_code=status.HTTP_202_ACCEPTED)
            case Failure(e):
                logging.exception("An error occurred while setting order status", e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error setting Order Status",
                )
            case x:
                raise AssertionError(f"Expected code to be unreachable {x}")

    def add_product(self: Self, product: Product) -> None:
        # Give the include a prefix from the product router
        product_router = ProductRouter(product, self)
        self.include_router(product_router, prefix=f"/products/{product.id}")
        self.product_routers[product.id] = product_router

    def generate_order_href(self: Self, request: Request, order_id: str) -> URL:
        return request.url_for(f"{self.name}:get-order", order_id=order_id)

    def generate_order_statuses_href(
        self: Self, request: Request, order_id: str
    ) -> URL:
        return request.url_for(f"{self.name}:list-order-statuses", order_id=order_id)

    def add_order_links(self, order: Order, request: Request):
        order.links.append(
            Link(
                href=str(self.generate_order_href(request, order.id)),
                rel="self",
                type=TYPE_GEOJSON,
            )
        )
        order.links.append(
            Link(
                href=str(self.generate_order_statuses_href(request, order.id)),
                rel="monitor",
                type=TYPE_JSON,
            ),
        )
