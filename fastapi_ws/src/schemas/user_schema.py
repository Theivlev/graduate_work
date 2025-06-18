from uuid import UUID

from pydantic import BaseModel
from src.schemas.dto import AbstractDTO


class UserCreate(AbstractDTO):
    """Схема создания пользователя."""

    name: str
    role: str = "user"
    room_id: UUID


class UserResponse(UserCreate):
    """Схема ответа пользователя."""

    id: UUID


class SuperuserResponse(UserResponse):
    """Схема ответа суперпользователя."""

    is_superuser: bool


class GetUserInfoResponse(BaseModel):
    """Схема пользователя из gRPC."""

    name: str = ""
    surname: str = ""
    patronymic: str = ""
    email: str
