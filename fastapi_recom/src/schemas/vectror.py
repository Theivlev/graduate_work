from uuid import UUID
from typing import Dict

from .dto import AbstractDTO


class UserVectorBase(AbstractDTO):
    user_id: UUID
    vector_data: Dict[str, float]


class UserVectorCreate(UserVectorBase):
    pass


class UserVectorSchema(UserVectorBase):
    pass


class MovieVectorBase(AbstractDTO):
    movie_id: UUID
    vector_data: Dict[str, float]


class MovieVectorCreate(MovieVectorBase):
    pass


class MovieVectorSchema(MovieVectorBase):
    pass
