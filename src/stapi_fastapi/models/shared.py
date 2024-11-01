from typing import Any, Self

from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    SerializerFunctionWrapHandler,
    model_serializer,
)


class Link(BaseModel):
    href: AnyUrl
    rel: str
    type: str | None = None
    title: str | None = None
    method: str | None = None
    headers: dict[str, str | list[str]] | None = None
    body: Any = None

    model_config = ConfigDict(extra="allow")

    # redefining init is a hack to get str type to validate for `href`,
    # as str is ultimately coerced into an AnyUrl automatically anyway
    def __init__(self, href: AnyUrl | str, **kwargs):
        super().__init__(href=href, **kwargs)

    # overriding the default serialization to filter None field values from
    # dumped json
    @model_serializer(mode="wrap", when_used="json")
    def serialize(self: Self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        return {k: v for k, v in handler(self).items() if v is not None}
