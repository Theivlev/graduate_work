import uuid
from typing import Any, Dict, Literal
from uuid import UUID

from src.models.dto import AbstractDTO


class MessageGenericDTO(AbstractDTO):
    id: UUID
    user_id: str
    body: str
    recipient: str
    channel: Literal["email", "push", "sms"]
    data: Dict[str, Any]
    notification_queue: str = "generic"

    @staticmethod
    def create(user_data: dict, channel: str = "email") -> "MessageGenericDTO":
        """
        Создает объект MessageGenericDTO на основе данных.
        """
        try:
            if not all(key in user_data for key in ["user_id", "email", "message"]):
                raise ValueError("В user_data отсутствуют обязательные поля: user_id, email, message")

            body = user_data.get("message")

            return MessageGenericDTO(
                id=uuid.uuid4(),
                user_id=user_data.get("user_id"),
                body=body,
                recipient=user_data.get("email"),
                channel=channel,
                data=user_data.get("data", {}),
                notification_type="generic",
            )
        except Exception as e:
            raise ValueError(f"Ошибка при создании MessageGenericDTO: {str(e)}")
