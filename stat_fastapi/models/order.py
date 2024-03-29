from enum import Enum
from typing import Literal

from geojson_pydantic import Feature
from geojson_pydantic.geometries import Geometry
from pydantic import AwareDatetime, ConfigDict

from stat_fastapi.models.constraints import Constraints
from stat_fastapi.models.shared import Link
from stat_fastapi.types.datetime_interval import DatetimeInterval


class OrderPayload(Feature[Geometry, Constraints]):
    product_id: str


class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    finished = "finished"
    failed = "failed"
    expired = "expired"


class OrderProperties(Constraints):
    datetime: DatetimeInterval

    status: OrderStatus = OrderStatus.pending
    created_at: AwareDatetime
    updated_at: AwareDatetime

    model_config = ConfigDict(extra="allow")


class Order(Feature[Geometry, OrderProperties]):
    type: Literal["Feature"] = "Feature"
    product_id: str
    links: list[Link]
