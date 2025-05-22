from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field, validator
from src.models.bookmark import UserBookmarks
from src.models.dto import AbstractDTO


class UserBookmarkCreateDTO(AbstractDTO):
    movie_id: UUID
    user_id: UUID
    bookmarked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("bookmarked_at")
    def validate_bookmarked_at(cls, value):
        if value > datetime.now(timezone.utc):
            raise ValueError("Дата создания не может быть изменена в будущем")
        return value


class UserBookmarkResponse(BaseModel):
    id: str
    movie_id: str
    user_id: str
    bookmarked_at: datetime

    @validator("bookmarked_at")
    def ensure_timezone(cls, value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @staticmethod
    def from_bookmark(bookmark: UserBookmarks) -> "UserBookmarkResponse":
        return UserBookmarkResponse(
            id=str(bookmark.id),
            movie_id=str(bookmark.movie_id),
            user_id=str(bookmark.user_id),
            bookmarked_at=bookmark.bookmarked_at,
        )
