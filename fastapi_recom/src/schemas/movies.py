from uuid import UUID

from .dto import AbstractDTO


class MovieBase(AbstractDTO):
    pass


class MovieCreate(MovieBase):
    id: UUID


class MovieUpdate(MovieBase):
    pass


class MovieSchema(MovieBase):
    id: UUID
