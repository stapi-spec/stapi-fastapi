from typing import Any, Literal, Mapping

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry

from stat_fastapi.models.constraints import Constraints

OpportunityProperties = Mapping[str, Any]


class OpportunitySearch(Feature[Geometry, Constraints]):
    product_id: str


class Opportunity(Feature[Geometry, OpportunityProperties]):
    type: Literal["Feature"] = "Feature"
    constraints: Constraints


class OpportunityCollection(FeatureCollection[Opportunity]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
