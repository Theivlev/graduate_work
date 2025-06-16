from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class KafkaSendMessage(BaseModel):
    """Схема для отправки сообщения в kafka."""

    user_id: UUID
    movie_id: UUID | None = None
    action: str
    event_data: str
    event_time: datetime


class RabbitSendMessage(BaseModel):
    """Схема для отправки сообщения в rabbitmq."""

    user_id: str
    movie_id: str
    action: dict[str, str]
    event_data: str
    event_time: datetime
