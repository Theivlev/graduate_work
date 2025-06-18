from uuid import UUID, uuid4

from pydantic import Field, computed_field

from .dto import AbstractDTO


class UUIDMixin(AbstractDTO):
    """Миксин для генерации уникальных идентификаторов UUID."""

    id: UUID = Field(default_factory=uuid4)

    @computed_field(alias="_id")
    def el_id(self) -> UUID:
        """el_id всегда равен id."""
        return self.id
