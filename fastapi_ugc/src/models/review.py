from datetime import datetime, timezone
from uuid import UUID

from beanie import Document
from pydantic import Field
from src.models.mixins import PyObjectId


class UserReviews(Document):
    """Модель для коллекции 'user_reviews'."""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    movie_id: UUID
    user_id: UUID
    review_text: str
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "user_reviews"
