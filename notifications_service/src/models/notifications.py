from datetime import datetime
from enum import Enum
from uuid import UUID

from beanie import Document
from pydantic import Field
from src.models.mixins import PyObjectId


class DeliveryMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationRecord(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: UUID
    body: str
    recipient: str
    delivery_method: DeliveryMethod
    expiration_time: datetime

    class Settings:
        name = "notification_record"
