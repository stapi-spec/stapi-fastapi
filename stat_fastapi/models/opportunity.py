from typing import Literal, Optional

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel

from stat_fastapi.types.datetime_interval import DatetimeInterval
from stat_fastapi.types.filter import CQL2Filter


# Copied and modified from stack_pydantic.item.ItemProperties
class OpportunityProperties(BaseModel):
    datetime: DatetimeInterval
    product_id: str
    filter: Optional[CQL2Filter] = None


class OpportunitySearch(OpportunityProperties):
    geometry: Geometry


class Opportunity(Feature[Geometry, OpportunityProperties]):
    type: Literal["Feature"] = "Feature"


class OpportunityCollection(FeatureCollection[Opportunity]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
