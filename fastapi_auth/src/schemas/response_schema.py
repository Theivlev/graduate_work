from src.models.dto import AbstractDTO


class ResponseSchema(AbstractDTO):
    """Схема пустого ответа."""

    detail: str
