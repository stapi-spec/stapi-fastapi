from datetime import timedelta
from enum import Enum
from logging import basicConfig

from pydantic_settings import BaseSettings

from .models import Satellite

MOCKSAT1 = """MOCKSAT-1
1 99999U 24029BR  24061.50000000  .00001103  00000-0  33518-4 0  9998
2 99999 97.00000   0.7036 0003481   0.0000   0.3331 15.07816962  1778"""


class LogLevel(Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class Settings(BaseSettings):
    satellite: Satellite = Satellite(
        tle=MOCKSAT1, block_time=(timedelta(seconds=10), timedelta(seconds=10))
    )

    loglevel: LogLevel = LogLevel.INFO
    database: str = "sqlite://"

    @classmethod
    def load(cls) -> "Settings":
        settings = Settings()
        basicConfig(level=settings.loglevel.value)
        return settings
