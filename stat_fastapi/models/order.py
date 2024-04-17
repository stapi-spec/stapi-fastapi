from typing import Literal

from geojson_pydantic import Feature
from geojson_pydantic.geometries import Geometry

from stat_fastapi.models.opportunity import OpportunityProperties
from stat_fastapi.models.shared import Link


class Order(Feature[Geometry, OpportunityProperties]):
    type: Literal["Feature"] = "Feature"
    links: list[Link]
