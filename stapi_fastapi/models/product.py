from enum import Enum
from typing import Literal, Optional
from abc import ABC, abstractmethod
from fastapi import Request

from pydantic import AnyHttpUrl, BaseModel, Field

from stapi_fastapi.models.shared import Link
from stapi_fastapi.models.opportunity import Opportunity, OpportunityProperties, OpportunityRequest
from stapi_fastapi.models.order import Order


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


class Product(BaseModel, ABC):
    type: Literal["Product"] = "Product"
    conformsTo: list[str] = Field(default_factory=list)
    id: str
    title: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    license: str
    providers: list[Provider] = Field(default_factory=list)
    links: list[Link]
    parameters: OpportunityProperties

    @abstractmethod
    def search_opportunities(self, search: OpportunityRequest, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.

        Backends must validate search constraints and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        ...

    @abstractmethod
    def create_order(self, search: OpportunityRequest, request: Request) -> Order:
        """
        Create a new order.

        Backends must validate order payload and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        ...

class ProductsCollection(BaseModel):
    type: Literal["ProductCollection"] = "ProductCollection"
    links: list[Link] = Field(default_factory=list)
    products: list[Product]
