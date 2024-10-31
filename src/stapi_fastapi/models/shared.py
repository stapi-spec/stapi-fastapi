from typing import Any, Optional, Self, Union

from pydantic import AnyUrl, BaseModel, ConfigDict


class Link(BaseModel):
    href: AnyUrl
    rel: str
    type: str | None = None
    title: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[dict[str, Union[str, list[str]]]] = None
    body: Any = None

    model_config = ConfigDict(extra="allow")

    # redefining init is a hack to get str type to validate for `href`,
    # as str is ultimately coerced into an AnyUrl automatically anyway
    def __init__(self, href: AnyUrl | str, **kwargs):
        super().__init__(href=href, **kwargs)

    def model_dump_json(self: Self, *args, **kwargs) -> str:
        # TODO: this isn't working as expected and we get nulls in the output
        #       maybe need to override python dump too
        # forcing the call to model_dump_json to exclude unset fields by default
        kwargs["exclude_unset"] = kwargs.get("exclude_unset", True)
        return super().model_dump_json(*args, **kwargs)


class HTTPException(BaseModel):
    detail: str
