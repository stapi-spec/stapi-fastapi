from typing import Any

from stapi_fastapi.models.opportunity import OpportunityProperties
from stapi_fastapi.models.order import OrderParameters


class SpotlightOpportunityProperties(OpportunityProperties):
    off_nadir: int


class SpotlightOrderParameters(OrderParameters):
    s3_path: str | None = None


type link_dict = dict[str, Any]


def find_link(links: list[link_dict], rel: str) -> link_dict | None:
    return next((link for link in links if link["rel"] == rel), None)
