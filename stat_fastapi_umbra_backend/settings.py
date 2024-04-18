"""Settings for Umbra Backend"""

from enum import Enum
from logging import basicConfig

from pydantic_settings import BaseSettings


class LogLevel(Enum):
    """Log Level Enum"""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class Settings(BaseSettings):
    """Settings for Umbra Backend"""

    loglevel: LogLevel = LogLevel.INFO
    database: str = "sqlite://"
    umbra_api_url: str = "https://canopy.umbra.com"
    feasibility_url: str = "https://api.canopy.umbra.space/tasking/feasibilities"

    @classmethod
    def load(cls) -> "Settings":
        """Load method to get settings"""
        settings = Settings()
        basicConfig(level=settings.loglevel.value)
        return settings
