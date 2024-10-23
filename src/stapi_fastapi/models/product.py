from enum import Enum
from typing import Literal, Optional, Self

from pydantic import AnyHttpUrl, BaseModel, Field

from stapi_fastapi.backends.product_backend import ProductBackend
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


class Product(BaseModel):
    type: Literal["Product"] = "Product"
    conformsTo: list[str] = Field(default_factory=list)
    id: str
    title: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    license: str
    providers: list[Provider] = Field(default_factory=list)
    links: list[Link]
    constraints: JsonSchemaModel

    def __init__(self: Self, backend: ProductBackend, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = backend


class ProductsCollection(BaseModel):
    type: Literal["ProductCollection"] = "ProductCollection"
    links: list[Link] = Field(default_factory=list)
    products: list[Product]
