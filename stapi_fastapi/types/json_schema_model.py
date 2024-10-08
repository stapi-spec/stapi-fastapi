from typing import Annotated, Any, Type, TypeAlias

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


JsonSchemaModel: TypeAlias = Annotated[
    Type[BaseModel],
    PlainValidator(validate),
    PlainSerializer(serialize),
    WithJsonSchema({"type": "object"}),
]
