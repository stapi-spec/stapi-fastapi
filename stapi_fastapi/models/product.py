from enum import Enum
from typing import Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, Field

from stapi_fastapi.models.shared import Link
from stapi_fastapi.types.json_schema_model import JsonSchemaModel


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


class ProductMeta(BaseModel):
    conformsTo: list[str] = Field(default_factory=list)
    id: str
    title: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    license: str
    providers: list[Provider] = Field(default_factory=list)


class Product(ProductMeta):
    type: Literal["Product"] = "Product"
    links: list[Link]
    parameters: JsonSchemaModel


class ProductsCollection(BaseModel):
    type: Literal["ProductCollection"] = "ProductCollection"
    links: list[Link] = Field(default_factory=list)
    products: list[Product]
