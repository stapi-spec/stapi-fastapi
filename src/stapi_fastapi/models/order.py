from typing import Literal, TypeVar

from geojson_pydantic import Feature
from geojson_pydantic.geometries import Geometry
from pydantic import StrictInt, StrictStr

from stapi_fastapi.models.opportunity import OpportunityPropertiesBase
from stapi_fastapi.models.shared import Link

G = TypeVar("G", bound=Geometry)
P = TypeVar("P", bound=OpportunityPropertiesBase)


class Order(Feature[G, P]):
    # We need to enforce that orders have an id defined, as that is required to
    # retrieve them via the API
    id: StrictInt | StrictStr  # type: ignore
    type: Literal["Feature"] = "Feature"
    links: list[Link]
