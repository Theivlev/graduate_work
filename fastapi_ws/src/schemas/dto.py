from pydantic import BaseModel, ConfigDict


class AbstractDTO(BaseModel):
    """Абстрактная схема."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )
