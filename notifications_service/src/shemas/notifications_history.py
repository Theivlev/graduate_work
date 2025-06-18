from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, validator
from src.models.notifications import NotificationRecord


class NotificationRecordResponse(BaseModel):
    id: str
    user_id: UUID
    body: str
    recipient: str
    delivery_method: str
    expiration_time: datetime

    @validator("expiration_time")
    def ensure_timezone(cls, value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @staticmethod
    def from_history(notification_history: NotificationRecord) -> "NotificationRecordResponse":
        return NotificationRecordResponse(
            id=str(notification_history.id),
            user_id=notification_history.user_id,
            body=notification_history.body,
            recipient=notification_history.recipient,
            delivery_method=notification_history.delivery_method,
            expiration_time=notification_history.expiration_time,
        )
