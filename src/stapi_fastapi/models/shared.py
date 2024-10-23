from typing import Any, Optional, Union

from pydantic import AnyUrl, BaseModel, ConfigDict


class Link(BaseModel):
    href: AnyUrl
    rel: str
    type: Optional[str] = None
    title: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[dict[str, Union[str, list[str]]]] = None
    body: Any = None

    model_config = ConfigDict(extra="allow")


class HTTPException(BaseModel):
    detail: str
