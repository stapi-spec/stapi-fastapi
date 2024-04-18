from typing import Optional

from pydantic import AnyUrl, BaseModel, ConfigDict


class Link(BaseModel):
    href: AnyUrl
    rel: str
    type: Optional[str] = None
    title: Optional[str] = None
    method: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class HTTPException(BaseModel):
    detail: str
