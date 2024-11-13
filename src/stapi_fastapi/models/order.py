from typing import Literal, TypeVar, Generic, Any

from geojson_pydantic import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from stapi_fastapi.models.opportunity import OpportunityRequest, OpportunityProperties
from stapi_fastapi.models.shared import Link


class OrderParameters(BaseModel):
    model_config = ConfigDict(extra="allow")

P = TypeVar("P", bound=OrderParameters)
O = TypeVar("O", bound=OpportunityProperties)

class OrderRequest(OpportunityRequest, Generic[P]):
    order_parameters: P

class OrderProperties(BaseModel, Generic[O]):
    opportunity_properties: O
    order_parameters: dict[str, Any]


class Order(Feature[Geometry, OrderProperties]):
    # We need to enforce that orders have an id defined, as that is required to
    # retrieve them via the API
    id: StrictInt | StrictStr  # type: ignore
    type: Literal["Feature"] = "Feature"
    links: list[Link] = Field(default_factory=list)

class OrderCollection(FeatureCollection[Order]):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    links: list[Link] = Field(default_factory=list)
