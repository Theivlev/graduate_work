from dataclasses import dataclass
from http import HTTPStatus
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.crud.user_crud import UserCrud
from src.models.user import User
from src.schemas.role_schema import RoleGetFull
from src.services.role_service import RoleService
from src.db.postgres import get_async_session

from fastapi import HTTPException


async def get_user_service() -> "UserService":
    async_session = await get_async_session()
    return UserService(async_session)


@dataclass
class UserService:
    """Сервис для работы с пользователем."""

    session: AsyncSession
    user_crud: CRUDBase = UserCrud(User)

    async def get_roles(self, user_id: UUID) -> List[RoleGetFull]:
        """Функция для получения ролей пользователя."""
        user = await self.get_model(user_id)
        return [RoleGetFull.model_validate(role) for role in user.roles]

    async def add_role(self, user_id: UUID, role_id: UUID) -> None:
        """Функция для установки роли пользователю."""
        role = await RoleService(self.session).get_model(role_id)
        user = await self.get_model(user_id)
        role_ids = [role.id for role in user.roles]
        if role_id in role_ids:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User already has this role")
        user.roles.append(role)
        self.session.add(user)
        await self.session.commit()

    async def delete_role(self, user_id: UUID, role_id: UUID) -> None:
        """Функция для удаления роли у пользователя."""
        await RoleService(self.session).get_model(role_id)
        user = await self.get_model(user_id)
        role_ids = [role.id for role in user.roles]
        if role_id not in role_ids:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User does not have this role")
        user.roles = [role for role in user.roles if role.id != role_id]
        self.session.add(user)
        await self.session.commit()

    async def get_model(self, user_id: UUID) -> User:
        """Функция для получения пользователя по его id."""
        user = await self.user_crud.get(user_id, self.session)
        if user is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
        return user
