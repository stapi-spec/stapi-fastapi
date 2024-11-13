from typing import Generic, Literal, TypeVar

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from stapi_fastapi.models.opportunity import OpportunityProperties
from stapi_fastapi.models.shared import Link
from stapi_fastapi.types.datetime_interval import DatetimeInterval
from stapi_fastapi.types.filter import CQL2Filter


class OrderParameters(BaseModel):
    model_config = ConfigDict(extra="allow")


ORP = TypeVar("ORP", bound=OrderParameters)
OPP = TypeVar("OPP", bound=OpportunityProperties)


class OrderRequest(BaseModel, Generic[ORP]):
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: CQL2Filter | None = None

    order_parameters: ORP

    model_config = ConfigDict(strict=True)


class OrderProperties(BaseModel, Generic[OPP, ORP]):
    product_id: str
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: CQL2Filter | None = None

    opportunity_properties: OPP
    order_parameters: ORP

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
