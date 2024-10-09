from typing import Any, Mapping
from fastapi import HTTPException

class StapiException(HTTPException):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code, detail)

class ConstraintsException(Exception):
    detail: Mapping[str, Any] | None

    def __init__(self, detail: Mapping[str, Any] | None = None) -> None:
        super().__init__()
        self.detail = detail


class NotFoundException(Exception):
    pass
