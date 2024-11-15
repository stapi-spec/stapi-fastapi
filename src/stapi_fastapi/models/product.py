from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Literal, Optional, Self

from pydantic import AnyHttpUrl, BaseModel, Field

from stapi_fastapi.models.opportunity import OpportunityProperties
from stapi_fastapi.models.order import OrderParameters
from stapi_fastapi.models.shared import Link

if TYPE_CHECKING:
    from stapi_fastapi.backends.product_backend import ProductBackend


class ProviderRole(str, Enum):
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
    def __init__(self, url: AnyHttpUrl | str, **kwargs):
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
    _constraints: type[OpportunityProperties]
    _order_parameters: type[OrderParameters]
    _backend: ProductBackend

    def __init__(
        self,
        *args,
        backend: ProductBackend,
        constraints: type[OpportunityProperties],
        order_parameters: type[OrderParameters],
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._backend = backend
        self._constraints = constraints
        self._order_parameters = order_parameters

    @property
    def backend(self: Self) -> ProductBackend:
        return self._backend

    @property
    def constraints(self: Self) -> type[OpportunityProperties]:
        return self._constraints

    @property
    def order_parameters(self: Self) -> type[OrderParameters]:
        return self._order_parameters

    def with_links(self: Self, links: list[Link] | None = None) -> Self:
        if not links:
            return self

        new = deepcopy(self)
        new.links.extend(links)
        return new


class ProductsCollection(BaseModel):
    type_: Literal["ProductCollection"] = Field("ProductCollection", alias="type")
    links: list[Link] = Field(default_factory=list)
    products: list[Product]
