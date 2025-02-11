from typing import Annotated, Any

from pydantic import (
    BaseModel,
    PlainSerializer,
    PlainValidator,
    WithJsonSchema,
)


def validate(v: Any) -> Any:
    if not issubclass(v, BaseModel):
        raise RuntimeError("BaseModel class required")
    return v


def serialize(v: type[BaseModel]) -> dict[str, Any]:
    return v.model_json_schema()


type JsonSchemaModel = Annotated[
    type[BaseModel],
    PlainValidator(validate),
    PlainSerializer(serialize),
    WithJsonSchema({"type": "object"}),
]
