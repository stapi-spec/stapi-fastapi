from pydantic import BaseModel, Field

CORE = "https://stapi.example.com/v0.1.0/core"
OPPORTUNITIES = "https://stapi.example.com/v0.1.0/opportunities"


class Conformance(BaseModel):
    conforms_to: list[str] = Field(
        default_factory=list, serialization_alias="conformsTo"
    )
