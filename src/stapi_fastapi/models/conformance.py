from pydantic import BaseModel, Field

CORE = "https://stapi.example.com/v0.1.0/core"
OPPORTUNITIES = "https://stapi.example.com/v0.1.0/opportunities"


class Conformance(BaseModel):
    conforms_to: list[str] = Field(default_factory=list, alias="conformsTo")

    def __init__(
        self,
        *args,
        conforms_to: list[str],
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.conforms_to = conforms_to
