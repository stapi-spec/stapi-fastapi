from typing import Literal, TypeVar

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict, Field

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
    filter: CQL2Filter | None = None
    model_config = ConfigDict(strict=True)


G = TypeVar("G", bound=Geometry)
P = TypeVar("P", bound=OpportunityProperties)


class Opportunity(Feature[G, P]):
    type: Literal["Feature"] = "Feature"
    links: list[Link] = Field(default_factory=list)


class OpportunityCollection(FeatureCollection[Opportunity[G, P]]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    links: list[Link] = Field(default_factory=list)
