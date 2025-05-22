from datetime import datetime, timezone
from uuid import UUID

from beanie import Document
from pydantic import Field
from src.models.mixins import PyObjectId


class UserLikes(Document):
    """Модель для коллекции 'user_likes'."""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    movie_id: UUID
    user_id: UUID
    rating: int = Field(..., ge=1, le=10)
    liked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "user_likes"
