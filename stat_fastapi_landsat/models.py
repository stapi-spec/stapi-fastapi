from pydantic import ConfigDict

from stat_fastapi.models.constraints import Constraints as BaseConstraints
from stat_fastapi.models.opportunity import OpportunityRequest


class Constraints(BaseConstraints):
    model_config = ConfigDict(extra="forbid")


class ValidatedOpportunityRequest(OpportunityRequest):
    properties: Constraints
