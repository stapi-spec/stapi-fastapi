from pydantic import BaseModel

from stat_fastapi.models.shared import Link


class RootResponse(BaseModel):
    links: list[Link]
