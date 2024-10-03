from pydantic import BaseModel, ConfigDict


class Constraints(BaseModel):
    model_config = ConfigDict(extra="allow")
