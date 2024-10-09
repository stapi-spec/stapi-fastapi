from typing import Literal, Optional, TypeVar, Generic

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict

from stapi_fastapi.types.datetime_interval import DatetimeInterval
from stapi_fastapi.types.filter import CQL2Filter

# Generic type definition for Opportunity Properties
T = TypeVar("T")

# Copied and modified from https://github.com/stac-utils/stac-pydantic/blob/main/stac_pydantic/item.py#L11
class OpportunityProperties(BaseModel, Generic[T]):
    datetime: DatetimeInterval
    model_config = ConfigDict(extra="allow")

class OpportunityRequest(BaseModel):
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: Optional[CQL2Filter] = None
    # PHILOSOPH: strict?

# Generic type definition for Opportunity
P = TypeVar("P", bound=OpportunityProperties)
K = TypeVar("K", bound=Geometry)

# Each product implements its own opportunity model
class Opportunity(Feature[K, P], Generic[K, P]):
    type: Literal["Feature"] = "Feature"


class OpportunityCollection(FeatureCollection[Opportunity]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
