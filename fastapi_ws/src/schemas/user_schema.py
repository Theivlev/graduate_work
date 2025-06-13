from uuid import UUID

from src.models.dto import AbstractDTO


class UserCreate(AbstractDTO):
    name: str
    role: str = "user"
    room_id: UUID


class UserResponse(UserCreate):
    id: UUID
