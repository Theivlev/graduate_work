from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MovieBaseDTO(BaseModel):
    """Базовая информация о фильме."""

    id: UUID
    title: str

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )
