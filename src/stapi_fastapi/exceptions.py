from typing import Any, Mapping


class ConstraintsException(Exception):
    detail: Mapping[str, Any] | None

    def __init__(self, detail: Mapping[str, Any] | None = None) -> None:
        super().__init__()
        self.detail = detail


class NotFoundException(Exception):
    pass
