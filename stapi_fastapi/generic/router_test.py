from pytest import mark

from stapi_fastapi.generic.models.product import BaseProductDeclaration
from stapi_fastapi.generic.router import RouterBase
from stapi_fastapi.models.product import ProductMeta


class ProductA(BaseProductDeclaration):
    product_meta = ProductMeta(id="product-a", license="")


class ProductB(BaseProductDeclaration):
    product_meta = ProductMeta(id="product-b", license="")


class ListRouter(RouterBase[list[ProductA, ProductB]]):
    """"""


class SingleRouter(RouterBase[ProductA]):
    """"""


@mark.parametrize(
    "cls, product_ids",
    (
        (SingleRouter, set(["product-a"])),
        (ListRouter, set(["product-a", "product-b"])),
    ),
)
def test_router(cls, product_ids):
    router = cls()
    assert router.product_ids == product_ids
