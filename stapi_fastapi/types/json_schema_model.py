from typing import Annotated, Any, Type

from pydantic import (
    BaseModel,
    PlainSerializer,
    PlainValidator,
    WithJsonSchema,
)


def validate(v: Any):
    if not issubclass(v, BaseModel):
        raise RuntimeError("BaseModel class required")
    return v


def serialize(v: Type[BaseModel]) -> dict[str, Any]:
    return v.model_json_schema()


type JsonSchemaModel = Annotated[
    Type[BaseModel],
    PlainValidator(validate),
    PlainSerializer(serialize),
    WithJsonSchema({"type": "object"}),
]
