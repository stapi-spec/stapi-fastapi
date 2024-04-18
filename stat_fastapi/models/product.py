from enum import Enum
from typing import Literal, Optional

from pydantic import AnyHttpUrl, BaseModel

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
    conformsTo: list[str] = []
    id: str
    title: str = ""
    description: str = ""
    keywords: list[str] = []
    license: str
    providers: list[Provider] = []
    links: list[Link]
    parameters: JsonSchemaModel


class ProductsCollection(BaseModel):
    type: Literal["ProductCollection"] = "ProductCollection"
    products: list[Product]
