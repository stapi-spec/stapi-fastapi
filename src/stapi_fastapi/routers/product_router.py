from __future__ import annotations

import logging
import traceback
from typing import TYPE_CHECKING, Annotated, Self

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from geojson_pydantic.geometries import Geometry
from returns.maybe import Maybe, Some
from returns.result import Failure, Success

from stapi_fastapi.constants import TYPE_JSON
from stapi_fastapi.exceptions import ConstraintsException, NotFoundException
from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
    OpportunityRequest,
    OpportunitySearchRecord,
    Prefer,
)
from stapi_fastapi.models.order import Order, OrderPayload
from stapi_fastapi.models.product import Product
from stapi_fastapi.models.shared import Link
from stapi_fastapi.responses import GeoJSONResponse
from stapi_fastapi.types.json_schema_model import JsonSchemaModel

if TYPE_CHECKING:
    from stapi_fastapi.routers import RootRouter

logger = logging.getLogger(__name__)


def get_preference(prefer: str | None = Header(None)) -> str | None:
    if prefer is None:
        return None

    if prefer not in Prefer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Prefer header value: {prefer}",
        )

    return prefer


class ProductRouter(APIRouter):
    def __init__(
        self: Self,
        product: Product,
        root_router: RootRouter,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        if (
            root_router.supports_async_opportunity_search
            and not product.supports_async_opportunity_search
        ):
            raise ValueError(
                f"Product '{product.id}' must support async opportunity search since "
                f"the root router does",
            )

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
            payload: OrderPayload,
            request: Request,
            response: Response,
        ) -> Order:
            return await self.create_order(payload, request, response)

        _create_order.__annotations__["payload"] = OrderPayload[
            self.product.order_parameters  # type: ignore
        ]

        self.add_api_route(
            path="/orders",
            endpoint=_create_order,
            name=f"{self.root_router.name}:{self.product.id}:create-order",
            methods=["POST"],
            response_class=GeoJSONResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create an order for the product",
            tags=["Products"],
        )

        if product.supports_opportunity_search:
            self.add_api_route(
                path="/opportunities",
                endpoint=self.search_opportunities,
                name=f"{self.root_router.name}:{self.product.id}:search-opportunities",
                methods=["POST"],
                response_class=GeoJSONResponse,
                # unknown why mypy can't see the constraints property on Product, ignoring
                response_model=OpportunityCollection[
                    Geometry,
                    self.product.opportunity_properties,  # type: ignore
                ],
                summary="Search Opportunities for the product",
                tags=["Products"],
            )

        if root_router.supports_async_opportunity_search:
            self.add_api_route(
                path="/opportunities",
                endpoint=self.search_opportunities_async,
                name=f"{self.root_router.name}:{self.product.id}:search-opportunities",
                methods=["POST"],
                status_code=status.HTTP_201_CREATED,
                summary="Search Opportunities for the product",
                tags=["Products"],
            )

            self.add_api_route(
                path="/opportunities/{opportunity_collection_id}",
                endpoint=self.get_opportunity_collection,
                name=f"{self.root_router.name}:{self.product.id}:get-opportunity-collection",
                methods=["GET"],
                summary="Get an Opportunity Collection by ID",
                tags=["Products"],
            )

    def get_product(self: Self, request: Request) -> Product:
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
        self: Self,
        search: OpportunityRequest,
        request: Request,
        response: GeoJSONResponse,
        prefer: str | None = Depends(get_preference),
        next: Annotated[str | None, Body()] = None,
        limit: Annotated[int, Body()] = 10,
    ) -> OpportunityCollection:
        """
        Explore the opportunities available for a particular set of constraints
        """
        if (
            not self.root_router.supports_async_opportunity_search
            or prefer is Prefer.wait
        ):
            links: list[Link] = []
            match await self.product._search_opportunities(
                self,
                search,
                next,
                limit,
                request,
            ):
                case Success((features, Some(pagination_token))):
                    links.append(self.order_link(request))
                    body = {
                        "search": search.model_dump(mode="json"),
                        "next": pagination_token,
                        "limit": limit,
                    }
                    links.append(self.pagination_link(request, body))
                case Success((features, Nothing)):  # noqa: F841
                    links.append(self.order_link(request))
                case Failure(e) if isinstance(e, ConstraintsException):
                    raise e
                case Failure(e):
                    logger.error(
                        "An error occurred while searching opportunities: %s",
                        traceback.format_exception(e),
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error searching opportunities",
                    )
                case x:
                    raise AssertionError(f"Expected code to be unreachable {x}")

            if (
                prefer is Prefer.wait
                and self.root_router.supports_async_opportunity_search
            ):
                response.headers["Preference-Applied"] = "wait"

            return OpportunityCollection(features=features, links=links)

        raise AssertionError("Expected code to be unreachable")

    async def search_opportunities_async(
        self: Self,
        search: OpportunityRequest,
        request: Request,
        response: Response,
        prefer: str | None = Depends(get_preference),
    ) -> OpportunitySearchRecord:
        """
        Initiate an asynchronous search for opportunities.

        TODO: Do I need a location header somewhere?
        """
        if (
            prefer is None
            or prefer is Prefer.respond_async
            or (prefer is Prefer.wait and not self.product.supports_opportunity_search)
        ):
            match await self.product._search_opportunities_async(self, search, request):
                case Success(search_record):
                    self.root_router.add_opportunity_search_record_self_link(
                        search_record, request
                    )
                    response.headers["Location"] = str(
                        self.root_router.generate_opportunity_search_record_href(
                            request, search_record.id
                        )
                    )
                    if prefer is not None:
                        response.headers["Preference-Applied"] = "respond-async"
                    return search_record
                case Failure(e) if isinstance(e, ConstraintsException):
                    raise e
                case Failure(e):
                    logger.error(
                        "An error occurred while initiating an asynchronous opportunity search: %s",
                        traceback.format_exception(e),
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error initiating an asynchronous opportunity search",
                    )
                case x:
                    raise AssertionError(f"Expected code to be unreachable: {x}")

        raise AssertionError("Expected code to be unreachable")

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
        self, payload: OrderPayload, request: Request, response: Response
    ) -> Order:
        """
        Create a new order.
        """
        match await self.product.create_order(
            self,
            payload,
            request,
        ):
            case Success(order):
                self.root_router.add_order_links(order, request)
                location = str(self.root_router.generate_order_href(request, order.id))
                response.headers["Location"] = location
                return order
            case Failure(e) if isinstance(e, ConstraintsException):
                raise e
            case Failure(e):
                logger.error(
                    "An error occurred while creating order: %s",
                    traceback.format_exception(e),
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error creating order",
                )
            case x:
                raise AssertionError(f"Expected code to be unreachable {x}")

    def order_link(self, request: Request):
        return Link(
            href=str(
                request.url_for(
                    f"{self.root_router.name}:{self.product.id}:create-order",
                ),
            ),
            rel="create-order",
            type=TYPE_JSON,
            method="POST",
        )

    def pagination_link(self, request: Request, body: dict[str, str | dict]):
        return Link(
            href=str(request.url.remove_query_params(keys=["next", "limit"])),
            rel="next",
            type=TYPE_JSON,
            method="POST",
            body=body,
        )

    async def get_opportunity_collection(
        self: Self, opportunity_collection_id: str, request: Request
    ) -> Response:
        """
        Fetch an opportunity collection generated by an asynchronous opportunity search.
        """
        match await self.product._get_opportunity_collection(
            self,
            opportunity_collection_id,
            request,
        ):
            case Success(Some(opportunity_collection)):
                opportunity_collection.links.append(
                    Link(
                        href=str(
                            request.url_for(
                                f"{self.root_router.name}:{self.product.id}:get-opportunity-collection",
                                opportunity_collection_id=opportunity_collection_id,
                            ),
                        ),
                        rel="self",
                        type=TYPE_JSON,
                    ),
                )
                return GeoJSONResponse(content=opportunity_collection.model_dump_json())
            case Success(Maybe.empty):
                raise NotFoundException("Opportunity Collection not found")
            case Failure(e):
                logger.error(
                    "An error occurred while fetching opportunity collection: '%s': %s",
                    opportunity_collection_id,
                    traceback.format_exception(e),
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error fetching Opportunity Collection",
                )
            case x:
                raise AssertionError(f"Expected code to be unreachable {x}")
