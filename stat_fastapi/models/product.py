from enum import Enum
from typing import Any, Literal, Mapping, Optional

from pydantic import AnyHttpUrl, AnyUrl, BaseModel

from stat_fastapi.constants import STAT_VERSION

from .shared import Link


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


class Product(BaseModel):
    type: Literal["Product"] = "Product"
    stat_version: str = STAT_VERSION
    stat_extensions: Optional[list[AnyUrl]] = None
    id: str
    title: Optional[str] = None
    description: str
    keywords: Optional[list[str]] = None
    license: str
    providers: list[Provider]
    links: list[Link]
    constraints: Optional[Mapping[str, Any]] = None  # TODO: Don't cheat


class ProductsCollection(BaseModel):
    type: Literal["ProductCollection"] = "ProductCollection"
    products: list[Product]
