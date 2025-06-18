from datetime import datetime, timezone
from uuid import UUID

from pydantic import Field

from src.models.base import BaseDocument
from src.models.mixins import PyObjectId


class UserBookmarks(BaseDocument):
    """
    Модель для коллекции 'user_bookmarks'.
    """

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    movie_id: UUID
    user_id: UUID
    bookmarked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "user_bookmarks"
