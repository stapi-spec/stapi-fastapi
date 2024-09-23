from typing import ClassVar, TypeVar

from pydantic import BaseModel

from stapi_fastapi.models.product import ProductMeta


# base class for product declarations: specify the product constraints and make
# sure to add a `ProductMeta` as the `product_meta` to describe the product in
# subclasses of this, then provide them to a custom subclass of `RouterBase`.
class BaseProductDeclaration(BaseModel):
    product_meta: ClassVar[ProductMeta]


ProductDeclaration = TypeVar("ProductDeclaration", bound=BaseProductDeclaration)
