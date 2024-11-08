from typing import Literal

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from stapi_fastapi.models.shared import Link
from stapi_fastapi.types.datetime_interval import DatetimeInterval


class OrderProperties(BaseModel):
    datetime: DatetimeInterval
    model_config = ConfigDict(extra="allow")


class Order(Feature[Geometry, OrderProperties]):
    # We need to enforce that orders have an id defined, as that is required to
    # retrieve them via the API
    id: StrictInt | StrictStr
    type: Literal["Feature"] = "Feature"
    links: list[Link] = Field(default_factory=list)


class OrderCollection(FeatureCollection[Order]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    links: list[Link] = Field(default_factory=list)
