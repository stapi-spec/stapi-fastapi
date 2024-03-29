from pydantic import BaseModel, ConfigDict

from stat_fastapi.types.datetime_interval import DatetimeInterval


class Constraints(BaseModel):
    datetime: DatetimeInterval

    model_config = ConfigDict(extra="allow")
