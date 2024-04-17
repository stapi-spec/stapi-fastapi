from typing import Any, Literal, Mapping

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry

from pydantic import BaseModel

from stat_fastapi.models.constraints import Constraints
from stat_fastapi.types import DatetimeInterval

# Copied and modified from stack_pydantic.item.ItemProperties
class OpportunityProperties(BaseModel):
    datetime: DatetimeInterval
    product_id: str
    constraints: Constraints

class OpportunitySearch(OpportunityProperties):
    geometry: Geometry

class Opportunity(Feature[Geometry, OpportunityProperties]):
    type: Literal["Feature"] = "Feature"

class OpportunityCollection(FeatureCollection[Opportunity]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
