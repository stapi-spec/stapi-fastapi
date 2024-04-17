from typing import Literal

from geojson_pydantic import Feature
from geojson_pydantic.geometries import Geometry

from stat_fastapi.models.constraints import Constraints
from stat_fastapi.models.shared import Link


class Order(Feature[Geometry, Constraints]):
    type: Literal["Feature"] = "Feature"
    product_id: str
    links: list[Link]
