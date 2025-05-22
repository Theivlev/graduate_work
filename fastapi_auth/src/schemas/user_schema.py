from uuid import UUID

from fastapi_users import schemas


class UserRead(schemas.BaseUser[UUID]):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None


class UserCreate(schemas.BaseUserCreate):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
