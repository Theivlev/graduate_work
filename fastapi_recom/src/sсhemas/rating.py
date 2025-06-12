from datetime import datetime
from uuid import UUID

from .dto import AbstractDTO


class RatingBase(AbstractDTO):
    rating: int
    timestamp: datetime | None = None


class RatingCreate(RatingBase):
    id: UUID
    user_id: UUID
    movie_id: UUID


class RatingUpdate(RatingBase):
    pass


class RatingSchema(RatingBase):
    id: UUID
    user_id: UUID
    movie_id: UUID
