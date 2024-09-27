from copy import copy
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
    """
    Product metadata
    """

    conformsTo: list[str] = Field(default_factory=list)
    id: str
    title: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    license: str
    providers: list[Provider] = Field(default_factory=list)
    parameters: JsonSchemaModel


class Product(ProductMeta):
    """
    Product schema for JSON responses
    """

    type: Literal["Product"] = "Product"
    links: list[Link]

    @classmethod
    def from_meta(cls, meta: ProductMeta, links: list[Link] = []):
        attribs = copy(meta.__dict__)
        attribs |= {"links": links}
        return cls(**attribs)


class ProductsCollection(BaseModel):
    """
    Products collection schema for JSON responses
    """

    type: Literal["ProductCollection"] = "ProductCollection"
    links: list[Link] = Field(default_factory=list)
    products: list[Product]
