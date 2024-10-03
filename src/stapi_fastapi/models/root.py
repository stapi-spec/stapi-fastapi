from pydantic import BaseModel

from stapi_fastapi.models.shared import Link


class RootResponse(BaseModel):
    links: list[Link]
