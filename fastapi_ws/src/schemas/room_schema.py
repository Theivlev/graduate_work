# src/schemas/room_schema.py
from typing import List, Optional
from uuid import UUID

from src.models.dto import AbstractDTO


class RoomCreate(AbstractDTO):
    name: str


class RoomResponse(RoomCreate):
    id: UUID
    message_history: Optional[List[dict]] = []
