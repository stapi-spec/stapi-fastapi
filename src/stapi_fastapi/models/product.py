from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Literal, Optional, Self

from pydantic import AnyHttpUrl, BaseModel, Field

from stapi_fastapi.models.opportunity import OpportunityProperties
from stapi_fastapi.models.order import OrderParameters
from stapi_fastapi.models.shared import Link

if TYPE_CHECKING:
    from stapi_fastapi.backends.product_backend import (
        CreateOrder,
        GetOpportunityCollection,
        SearchOpportunities,
        SearchOpportunitiesAsync,
    )


type Constraints = BaseModel


class ProviderRole(StrEnum):
    licensor = "licensor"
    producer = "producer"
    processor = "processor"
    host = "host"


class Provider(BaseModel):
    name: str
    description: Optional[str] = None
    roles: list[ProviderRole]
    url: AnyHttpUrl

    # redefining init is a hack to get str type to validate for `url`,
    # as str is ultimately coerced into an AnyHttpUrl automatically anyway
    def __init__(self, url: AnyHttpUrl | str, **kwargs) -> None:
        super().__init__(url=url, **kwargs)


class Product(BaseModel):
    type_: Literal["Product"] = Field(default="Product", alias="type")
    conformsTo: list[str] = Field(default_factory=list)
    id: str
    title: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    license: str
    providers: list[Provider] = Field(default_factory=list)
    links: list[Link] = Field(default_factory=list)

    # we don't want to include these in the model fields
    _constraints: type[Constraints]
    _opportunity_properties: type[OpportunityProperties]
    _order_parameters: type[OrderParameters]
    _create_order: CreateOrder
    _search_opportunities: SearchOpportunities | None
    _search_opportunities_async: SearchOpportunitiesAsync | None
    _get_opportunity_collection: GetOpportunityCollection | None

    def __init__(
        self,
        *args,
        constraints: type[Constraints],
        opportunity_properties: type[OpportunityProperties],
        order_parameters: type[OrderParameters],
        create_order: CreateOrder,
        search_opportunities: SearchOpportunities | None = None,
        search_opportunities_async: SearchOpportunitiesAsync | None = None,
        get_opportunity_collection: GetOpportunityCollection | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        if bool(search_opportunities_async) != bool(get_opportunity_collection):
            raise ValueError(
                "Both the `search_opportunities_async` and `get_opportunity_collection` "
                "arguments must be provided if either is provided"
            )

        self._constraints = constraints
        self._opportunity_properties = opportunity_properties
        self._order_parameters = order_parameters
        self._create_order = create_order
        self._search_opportunities = search_opportunities
        self._search_opportunities_async = search_opportunities_async
        self._get_opportunity_collection = get_opportunity_collection

    @property
    def create_order(self) -> CreateOrder:
        return self._create_order

    @property
    def search_opportunities(self) -> SearchOpportunities:
        if not self._search_opportunities:
            raise AttributeError("This product does not support opportunity search")
        return self._search_opportunities

    @property
    def search_opportunities_async(self) -> SearchOpportunitiesAsync:
        if not self._search_opportunities_async:
            raise AttributeError(
                "This product does not support async opportunity search"
            )
        return self._search_opportunities_async

    @property
    def get_opportunity_collection(self) -> GetOpportunityCollection:
        if not self._get_opportunity_collection:
            raise AttributeError(
                "This product does not support async opportunity search"
            )
        return self._get_opportunity_collection

    @property
    def constraints(self) -> type[Constraints]:
        return self._constraints

    @property
    def opportunity_properties(self) -> type[OpportunityProperties]:
        return self._opportunity_properties

    @property
    def order_parameters(self) -> type[OrderParameters]:
        return self._order_parameters

    @property
    def supports_opportunity_search(self) -> bool:
        return self._search_opportunities is not None

    @property
    def supports_async_opportunity_search(self) -> bool:
        return (
            self._search_opportunities_async is not None
            and self._get_opportunity_collection is not None
        )

    def with_links(self, links: list[Link] | None = None) -> Self:
        if not links:
            return self

        new = self.model_copy(deep=True)
        new.links.extend(links)
        return new


class ProductsCollection(BaseModel):
    type_: Literal["ProductCollection"] = Field(
        default="ProductCollection", alias="type"
    )
    links: list[Link] = Field(default_factory=list)
    products: list[Product]
