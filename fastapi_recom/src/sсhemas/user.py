from uuid import UUID

from .dto import AbstractDTO


class UserBase(AbstractDTO):
    pass


class UserCreate(UserBase):
    id: UUID


class UserUpdate(UserBase):
    pass


class UserSchema(UserBase):
    id: UUID
