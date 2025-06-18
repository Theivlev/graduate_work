from dataclasses import dataclass
from http import HTTPStatus
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.db.postgres import get_async_session
from src.models.role import Role
from src.schemas.role_schema import RoleCreate, RoleGetFull, RoleUpdate

from fastapi import Depends, HTTPException


def get_role_service(session: AsyncSession = Depends(get_async_session)) -> "RoleService":
    """Функция для получения сервиса ролей."""
    return RoleService(session)


@dataclass
class RoleService:
    """Сервис для работы с ролями."""

    session: AsyncSession
    role_crud: CRUDBase = CRUDBase(Role)

    async def get_all(self) -> List[RoleGetFull]:
        """Получение списка ролей."""
        roles_obj = await self.role_crud.get_multi(self.session)
        return [RoleGetFull.model_validate(role_obj) for role_obj in roles_obj]

    async def create(self, data: RoleCreate) -> RoleGetFull:
        """Создание новой роли."""
        role_obj = await self.role_crud.create(data, self.session)
        return RoleGetFull.model_validate(role_obj)

    async def update(self, role_id: UUID, data: RoleUpdate) -> RoleGetFull:
        """Обновление роли."""
        role = await self.get_model(role_id)
        role_obj = await self.role_crud.update(role, data, self.session)
        return RoleGetFull.model_validate(role_obj)

    async def delete(self, role_id: UUID) -> None:
        """Удаление роли."""
        role = await self.get_model(role_id)
        await self.role_crud.remove(role, self.session)

    async def get_model(self, role_id: UUID) -> Role:
        """Получение роли по id."""
        role = await self.role_crud.get(role_id, self.session)
        if role is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
        return role
