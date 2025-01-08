from enum import StrEnum
from typing import Any, Dict, Generic, Iterator, Literal, Optional, TypeVar, Union

from geojson_pydantic.base import _GeoJsonBase
from geojson_pydantic.geometries import Geometry
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictStr,
    field_validator,
)

from stapi_fastapi.models.opportunity import OpportunityProperties
from stapi_fastapi.models.shared import Link
from stapi_fastapi.types.datetime_interval import DatetimeInterval
from stapi_fastapi.types.filter import CQL2Filter

Props = TypeVar("Props", bound=Union[Dict[str, Any], BaseModel])
Geom = TypeVar("Geom", bound=Geometry)


class OrderParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")


OPP = TypeVar("OPP", bound=OpportunityProperties)
ORP = TypeVar("ORP", bound=OrderParameters)


class OrderStatusCode(StrEnum):
    received = "received"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"
    canceled = "canceled"


class OrderStatus(BaseModel):
    timestamp: AwareDatetime
    status_code: OrderStatusCode
    reason_code: Optional[str] = None
    reason_text: Optional[str] = None
    links: list[Link] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class OrderStatuses[T: OrderStatus](BaseModel):
    statuses: list[T]
    links: list[Link] = Field(default_factory=list)


class OrderSearchParameters(BaseModel):
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: CQL2Filter | None = None


class OrderProperties[T: OrderStatus](BaseModel):
    product_id: str
    created: AwareDatetime
    status: T

    search_parameters: OrderSearchParameters
    opportunity_properties: dict[str, Any]
    order_parameters: dict[str, Any]

    model_config = ConfigDict(extra="allow")


# derived from geojson_pydantic.Feature
class Order(_GeoJsonBase):
    # We need to enforce that orders have an id defined, as that is required to
    # retrieve them via the API
    id: StrictStr
    type: Literal["Feature"] = "Feature"

    geometry: Geometry = Field(...)
    properties: OrderProperties = Field(...)

    links: list[Link] = Field(default_factory=list)

    __geojson_exclude_if_none__ = {"bbox", "id"}

    @field_validator("geometry", mode="before")
    def set_geometry(cls, geometry: Any) -> Any:
        """set geometry from geo interface or input"""
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__

        return geometry


# derived from geojson_pydantic.FeatureCollection
class OrderCollection(_GeoJsonBase):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[Order]
    links: list[Link] = Field(default_factory=list)

    def __iter__(self) -> Iterator[Order]:  # type: ignore [override]
        """iterate over features"""
        return iter(self.features)

    def __len__(self) -> int:
        """return features length"""
        return len(self.features)

    def __getitem__(self, index: int) -> Order:
        """get feature at a given index"""
        return self.features[index]


class OrderPayload(BaseModel, Generic[ORP]):
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: CQL2Filter | None = None

    order_parameters: ORP

    model_config = ConfigDict(strict=True)
