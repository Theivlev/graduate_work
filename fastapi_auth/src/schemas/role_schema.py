from typing import List
from uuid import UUID

from pydantic import field_validator
from src.models.dto import AbstractDTO
from src.models.role import Permissions


class RoleCreate(AbstractDTO):
    """Схема для создания роли."""

    name: str
    permissions: List[Permissions]

    @field_validator("permissions")
    def _check_permissions(cls, v):
        if v is None:
            return None
        if len(v) == 0:
            raise ValueError("Permissions can't be empty")
        return v


class RoleUpdate(AbstractDTO):
    """Схема для обновления роли."""

    name: str | None = None
    permissions: List[Permissions] | None = None


class RoleGetFull(RoleCreate):
    """Схема для получения полной информации о роли."""

    id: UUID


class UserRoleCreate(AbstractDTO):
    """Схема для создания роли пользователя."""

    user_id: UUID
    role_id: UUID
