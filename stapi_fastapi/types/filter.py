from typing import Annotated, TypeAlias

from pydantic import BeforeValidator
from pygeofilter.parsers import cql2_json


def validate(v: dict):
    if v:
        try:
            cql2_json.parse({"filter": v})
        except Exception as e:
            raise ValueError("Filter is not valid cql2-json") from e
    return v

CQL2Filter: TypeAlias = Annotated[
    dict,
    BeforeValidator(validate),
]
