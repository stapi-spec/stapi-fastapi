from typing import Annotated

from pydantic import BeforeValidator
from pygeofilter.parsers import cql2_json


def validate(v: dict):
    if v:
        try:
            cql2_json.parse({"filter": v})
        except Exception as e:
            raise ValueError("Filter is not valid cql2-json") from e
    return v


type CQL2Filter = Annotated[
    dict,
    BeforeValidator(validate),
]
