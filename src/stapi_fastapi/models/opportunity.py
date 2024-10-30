from typing import Literal, Optional

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict

from stapi_fastapi.models.shared import Link
from stapi_fastapi.types.datetime_interval import DatetimeInterval
from stapi_fastapi.types.filter import CQL2Filter


# Copied and modified from https://github.com/stac-utils/stac-pydantic/blob/main/stac_pydantic/item.py#L11
class OpportunityProperties(BaseModel):
    datetime: DatetimeInterval
    model_config = ConfigDict(extra="allow")


class OpportunityRequest(BaseModel):
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: Optional[CQL2Filter] = None
    model_config = ConfigDict(strict=True)


# GENERIC: Each product needs an opportunity model (constraints/parameters)
class Opportunity(Feature[Geometry, OpportunityProperties]):
    type: Literal["Feature"] = "Feature"
    links: list[Link] = []


class OpportunityCollection(FeatureCollection[Opportunity]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
