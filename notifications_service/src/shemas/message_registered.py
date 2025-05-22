import uuid
from typing import Literal
from uuid import UUID

from src.models.dto import AbstractDTO


class MessageRegisteredDTO(AbstractDTO):
    id: UUID
    user_id: str
    body: str
    recipient: str
    channel: Literal["email"]
    notification_queue: str = "user_registered"

    @staticmethod
    def create(user_data: dict) -> "MessageRegisteredDTO":
        """
        Создает объект MessageRegisteredDTO на основе данных пользователя.
        """
        try:
            if not all(key in user_data for key in ["user_id", "email"]):
                raise ValueError("Отсутствуют обязательные поля: user_id, email")
            return MessageRegisteredDTO(
                id=uuid.uuid4(),
                user_id=user_data.get("user_id"),
                body="Welcome to our service!",
                recipient=user_data.get("email"),
                channel="email",
                notification_type="user_registered",
            )
        except Exception as e:
            raise ValueError(f"Ошибка при создании MessageRegisteredDTO: {str(e)}")
