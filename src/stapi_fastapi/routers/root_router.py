import logging
import traceback
from typing import Self

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.datastructures import URL
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
)
from stapi_fastapi.models.product import Product, ProductsCollection
from stapi_fastapi.models.root import RootResponse
from stapi_fastapi.models.shared import Link
from stapi_fastapi.responses import GeoJSONResponse
from stapi_fastapi.routers.product_router import ProductRouter

logger = logging.getLogger(__name__)


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

    def get_products(
        self, request: Request, next: str | None = None, limit: int = 10
    ) -> ProductsCollection:
        start = 0
        product_ids = [*self.product_routers.keys()]
        try:
            if next:
                start = product_ids.index(next)
        except ValueError:
            logging.exception("An error occurred while retrieving orders")
            raise NotFoundException(detail="Error finding pagination token") from None
        end = min(start + limit, len(product_ids))
        ids = product_ids[start:end]
        links = [
            Link(
                href=str(request.url_for(f"{self.name}:list-products")),
                rel="self",
                type=TYPE_JSON,
            ),
        ]
        if end < len(product_ids):
            links.append(
                Link(
                    href=str(
                        request.url.include_query_params(
                            next=self.product_routers[product_ids[end]].product.id
                        ),
                    ),
                    rel="next",
                    type=TYPE_JSON,
                )
            )
        return ProductsCollection(
            products=[
                self.product_routers[product_id].get_product(request)
                for product_id in ids
            ],
            links=links,
        )

    async def get_orders(
        self, request: Request, next: str | None = None, limit: int = 10
    ) -> OrderCollection:
        match await self.backend.get_orders(request, next, limit):
            case Success((orders, pagination_token)):
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
                if pagination_token:
                    return OrderCollection(
                        features=orders,
                        links=[
                            Link(
                                href=str(
                                    request.url.include_query_params(
                                        next=pagination_token
                                    )
                                ),
                                rel="next",
                                type=TYPE_JSON,
                            )
                        ],
                    )
                return OrderCollection(features=orders)
            case Failure(e):
                logger.error(
                    "An error occurred while retrieving orders: %s",
                    traceback.format_exception(e),
                )
                if isinstance(e, ValueError):
                    raise NotFoundException(detail="Error finding pagination token")
                else:
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
                logger.error(
                    "An error occurred while retrieving order '%s': %s",
                    order_id,
                    traceback.format_exception(e),
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error finding Order",
                )
            case _:
                raise AssertionError("Expected code to be unreachable")

    async def get_order_statuses(
        self: Self,
        order_id: str,
        request: Request,
        next: str | None = None,
        limit: int = 10,
    ) -> OrderStatuses:
        match await self.backend.get_order_statuses(order_id, request, next, limit):
            case Success((statuses, pagination_token)):
                links = [
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
                ]
                if pagination_token:
                    links.append(
                        Link(
                            href=str(
                                request.url.include_query_params(next=pagination_token)
                            ),
                            rel="next",
                            type=TYPE_JSON,
                        )
                    )
                    return OrderStatuses(statuses=statuses, links=links)
                return OrderStatuses(
                    statuses=statuses,
                    links=links,
                )
            case Failure(e):
                logger.error(
                    "An error occurred while retrieving order statuses: %s",
                    traceback.format_exception(e),
                )
                if isinstance(e, KeyError):
                    raise NotFoundException(detail="Error finding pagination token")
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error finding Order Statuses",
                    )
            case _:
                raise AssertionError("Expected code to be unreachable")

    def add_product(self: Self, product: Product, *args, **kwargs) -> None:
        # Give the include a prefix from the product router
        product_router = ProductRouter(product, self, *args, **kwargs)
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
