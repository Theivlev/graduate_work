from typing import List, Optional
from uuid import UUID

from src.schemas.dto import AbstractDTO


class RoomCreate(AbstractDTO):
    """Схема создания комнаты."""

    name: str


class RoomResponse(RoomCreate):
    """Схема ответа комнаты."""

    id: UUID
    message_history: Optional[List[dict]] = []
