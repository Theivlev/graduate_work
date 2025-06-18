from uuid import UUID, uuid4

from pydantic import Field, field_serializer

from .dto import AbstractDTO


class UUIDMixin(AbstractDTO):
    """Миксин для генерации уникальных идентификаторов UUID."""

    id: UUID = Field(default_factory=uuid4)

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
