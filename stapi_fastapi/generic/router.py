from typing import Generic, List, TypeVar, get_args

from stapi_fastapi.generic.models.product import ProductDeclaration

ProductDeclarations = TypeVar(
    "ProductDeclaration", bound=List[ProductDeclaration] | ProductDeclaration
)


class RouterBase(Generic[ProductDeclarations]):
    """
    Generic router base class, supporting both a list of or a single product
    declaration to build fully documented endpoints dynamically.
    """

    _declarations: dict[str, ProductDeclaration]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # get products to support: build dict of product id to product
        # declaration
        declarations: tuple[ProductDeclaration]

        args = get_args(cls.__orig_bases__[0])[0]
        if isinstance(args, type(list[ProductDeclaration])):
            declarations = get_args(args)
        else:
            declarations = tuple([args])

        cls._declarations = {
            declaration.product_meta.id: declaration for declaration in declarations
        }

    def __init__(self):
        super().__init__()

        # TODO: build endpoints dynamically from product declarations, enabling
        # to generate full OpenAPI docs listing constraints for each product in
        # full detail.

    @property
    def product_ids(self):
        return set(self._declarations.keys())
