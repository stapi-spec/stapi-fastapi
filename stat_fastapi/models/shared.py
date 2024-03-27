from typing import Optional

from pydantic import AnyUrl, BaseModel


class Link(BaseModel):
    href: AnyUrl
    rel: str
    type: Optional[str] = None
    title: Optional[str] = None


class HTTPException(BaseModel):
    detail: str
