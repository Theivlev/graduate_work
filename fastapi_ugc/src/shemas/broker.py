from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BrokerSendMessage(BaseModel):
    """Схема для отправки сообщения в брокер."""

    user_id: UUID
    movie_id: UUID | None = None
    action: str
    event_data: str
    event_time: datetime
