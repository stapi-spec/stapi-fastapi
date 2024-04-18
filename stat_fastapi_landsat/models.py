from pydantic import (
    ConfigDict,
)

from stat_fastapi.models.constraints import Constraints as BaseConstraints
from stat_fastapi.models.opportunity import OpportunitySearch


class Constraints(BaseConstraints):
    model_config = ConfigDict(extra="forbid")


class ValidatedOpportunitySearch(OpportunitySearch):
    properties: Constraints
