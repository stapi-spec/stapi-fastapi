from typing import Annotated, Any, TypeAliasType

from pydantic import BeforeValidator
from pygeofilter.parsers import cql2_json


def validate(v: Any):
    if v:
        try:
            cql2_json.parse({"filter": v})
        except Exception as e:
            raise ValueError("Filter is not valid cql2-json") from e
    return v


CQL2Filter = TypeAliasType(
    "CQL2Filter",
    Annotated[
        dict,
        BeforeValidator(validate),
    ],
)
