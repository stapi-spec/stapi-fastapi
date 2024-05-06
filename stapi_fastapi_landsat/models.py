from pydantic import ConfigDict

from stapi_fastapi.models.constraints import Constraints as BaseConstraints
from stapi_fastapi.models.opportunity import OpportunityRequest


class Constraints(BaseConstraints):
    model_config = ConfigDict(extra="forbid")


class ValidatedOpportunityRequest(OpportunityRequest):
    properties: Constraints
