from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field, validator
from src.models.dto import AbstractDTO
from src.models.review import UserReviews


class UserReviewCreateDTO(AbstractDTO):
    movie_id: UUID
    user_id: UUID
    review_text: str
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("review_text")
    def validate_rating(cls, value):
        len_value = len(value)
        if len_value < 11:
            raise ValueError("Количество символов должно быть больше 10!")
        if len_value > 1000:
            raise ValueError("Количество символов должно быть меньше 1000!")
        return value

    @validator("reviewed_at")
    def validate_reviewed_at(cls, value):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value > datetime.now(timezone.utc):
            raise ValueError("Дата создания не может быть изменена в будущем")
        return value


class UserReviewResponse(BaseModel):
    id: str
    movie_id: str
    user_id: str
    reviewed_at: datetime
    review_text: str

    @validator("reviewed_at")
    def ensure_timezone(cls, value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @staticmethod
    def from_review(review: UserReviews) -> "UserReviewResponse":
        return UserReviewResponse(
            id=str(review.id),
            movie_id=str(review.movie_id),
            user_id=str(review.user_id),
            reviewed_at=review.reviewed_at,
            review_text=review.review_text,
        )
