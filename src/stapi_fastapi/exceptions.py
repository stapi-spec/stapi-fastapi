from typing import Any

from fastapi import HTTPException, status


class StapiException(HTTPException):
    pass


class ConstraintsException(StapiException):
    def __init__(self, detail: Any) -> None:
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail)


class NotFoundException(StapiException):
    def __init__(self, detail: Any) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail)
