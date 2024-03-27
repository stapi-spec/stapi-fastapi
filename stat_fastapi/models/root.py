from pydantic import BaseModel

from .shared import Link


class RootResponse(BaseModel):
    links: list[Link]
