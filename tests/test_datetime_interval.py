from datetime import UTC, datetime, timedelta
from itertools import product
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ValidationError
from pyrfc3339.utils import format_timezone
from pytest import mark, raises

from stapi_fastapi.types.datetime_interval import DatetimeInterval

EUROPE_BERLIN = ZoneInfo("Europe/Berlin")


class Model(BaseModel):
    datetime: DatetimeInterval


def rfc3339_strftime(dt: datetime, format: str) -> str:
    tds = int(round(dt.tzinfo.utcoffset(dt).total_seconds()))  # type: ignore
    long = format_timezone(tds)
    short = "Z"

    format = format.replace("%z", long).replace("%Z", short if tds == 0 else long)
    return dt.strftime(format)


@mark.parametrize(
    "value",
    (
        "",
        "2024-01-29/2024-01-30",
        "2024-01-29T12:00:00/2024-01-30T12:00:00",
        "2024-01-29T12:00:00Z/2024-01-28T12:00:00Z",
    ),
)
def test_invalid_values(value: str):
    with raises(ValidationError):
        Model.model_validate_strings({"datetime": value})


@mark.parametrize(
    "tz, format",
    product(
        (UTC, EUROPE_BERLIN),
        (
            "%Y-%m-%dT%H:%M:%S.%f%Z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S.%f%Z",
            "%Y-%m-%dt%H:%M:%S.%f%Z",
            "%Y-%m-%d_%H:%M:%S.%f%Z",
        ),
    ),
)
def test_deserialization(tz: ZoneInfo, format: str):
    start = datetime.now(tz)
    end = start + timedelta(hours=1)
    value = f"{rfc3339_strftime(start, format)}/{rfc3339_strftime(end, format)}"

    model = Model.model_validate_json(f'{{"datetime":"{value}"}}')

    assert model.datetime == (start, end)


@mark.parametrize("tz", (UTC, EUROPE_BERLIN))
def test_serialize(tz):
    start = datetime.now(tz)
    end = start + timedelta(hours=1)
    model = Model(datetime=(start, end))

    format = "%Y-%m-%dT%H:%M:%S.%f%z"
    expected = f"{rfc3339_strftime(start, format)}/{rfc3339_strftime(end, format)}"

    obj = model.model_dump()
    assert obj["datetime"] == expected
