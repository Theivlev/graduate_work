from typing import Any

from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """
    Пользовательский тип для MongoDB ObjectId, совместимый с Pydantic v2.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: Any) -> core_schema.CoreSchema:
        """
        Определяет схему валидации и сериализации для Pydantic v2.
        """
        return core_schema.with_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, value: Any, info: Any) -> ObjectId:
        """
        Валидирует входное значение как ObjectId.
        """
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        raise ValueError("Недопустимый ObjectId")
