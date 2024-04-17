from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from stat_fastapi.models.constraints import Constraints as BaseConstraints
from stat_fastapi.models.opportunity import OpportunitySearch
from stat_fastapi.models.order import OrderPayload

OFF_NADIR_RANGE = (0.0, 45.0)
OFF_NADIR_DEFAULT_RANGE = (0.0, 30.0)
OFF_NADIR_MIN_SPREAD = 5.0


class OffNadirRange(BaseModel):
    minimum: float = Field(ge=OFF_NADIR_RANGE[0], le=OFF_NADIR_RANGE[1])
    maximum: float = Field(ge=OFF_NADIR_RANGE[0], le=OFF_NADIR_RANGE[1])

    @model_validator(mode="after")
    def validate(self) -> "OffNadirRange":
        diff = self.maximum - self.minimum
        if diff < OFF_NADIR_MIN_SPREAD:
            raise ValueError(f"range must be at least {OFF_NADIR_MIN_SPREAD}°")
        return self


class Constraints(BaseConstraints):
    off_nadir: OffNadirRange = OffNadirRange(
        minimum=OFF_NADIR_DEFAULT_RANGE[0],
        maximum=OFF_NADIR_DEFAULT_RANGE[1],
    )

    model_config = ConfigDict(extra="forbid")


class ValidatedOpportunitySearch(OpportunitySearch):
    properties: Constraints


class ValidatedOrderPayload(OrderPayload):
    properties: Constraints
