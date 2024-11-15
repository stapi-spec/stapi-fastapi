from enum import Enum
from typing import Any, Generic, Literal, Optional, TypeVar

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
)

from stapi_fastapi.models.opportunity import OpportunityProperties
from stapi_fastapi.models.shared import Link
from stapi_fastapi.types.datetime_interval import DatetimeInterval
from stapi_fastapi.types.filter import CQL2Filter


class OrderParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")


OPP = TypeVar("OPP", bound=OpportunityProperties)
ORP = TypeVar("ORP", bound=OrderParameters)


class OrderRequest(BaseModel, Generic[ORP]):
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: CQL2Filter | None = None

    order_parameters: ORP

    model_config = ConfigDict(strict=True)


class OrderStatusCode(str, Enum):
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


class OrderSearchParameters(BaseModel):
    datetime: DatetimeInterval
    geometry: Geometry
    # TODO: validate the CQL2 filter?
    filter: CQL2Filter | None = None


class OrderProperties(BaseModel):
    product_id: str
    created: AwareDatetime
    status: OrderStatus

    search_parameters: OrderSearchParameters
    opportunity_properties: dict[str, Any]
    order_parameters: dict[str, Any]

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
