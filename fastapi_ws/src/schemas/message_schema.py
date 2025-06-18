# src/schemas/message_schema.py
from datetime import datetime
from uuid import UUID

from src.schemas.dto import AbstractDTO


class MessageCreate(AbstractDTO):
    text: str


class MessageResponse(MessageCreate):
    """Схема сообщений."""

    id: UUID
    created_at: datetime
    room_id: UUID
    user_id: UUID
