from enum import Enum
from typing import Literal, Optional

from pydantic import AnyHttpUrl, AnyUrl, BaseModel

from stat_fastapi.constants import STAT_VERSION
from stat_fastapi.types.json_schema_model import JsonSchemaModel

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
    constraints: JsonSchemaModel


class ProductsCollection(BaseModel):
    type: Literal["ProductCollection"] = "ProductCollection"
    products: list[Product]
