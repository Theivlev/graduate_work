from datetime import datetime
from uuid import UUID

from pydantic import Field
from src.models.mixins import UUIDMixin


class AuthGetHistory(UUIDMixin):
    """Модель истории авторизации пользователя."""

    user_id: UUID
    user_agent: str
    timestamp: datetime = Field(default=datetime.now())


class AuthCreateHistory(AuthGetHistory):
    user_device_type: str
