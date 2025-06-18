from uuid import UUID, uuid4

from pydantic import Field

from .dto import AbstractDTO


class UUIDMixin(AbstractDTO):
    """Миксин для генерации уникальных идентификаторов UUID."""

    id: UUID = Field(default_factory=uuid4)
