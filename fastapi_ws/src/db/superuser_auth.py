from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import get_async_session
from src.models.user_model import User
from src.schemas.user_schema import SuperuserResponse

from fastapi import Depends, HTTPException, status

api_key_scheme = APIKeyHeader(name="X-API-Key")


async def get_superuser(
    api_key: str = Depends(api_key_scheme), session: AsyncSession = Depends(get_async_session)
) -> SuperuserResponse:
    """Зависимость для аутентификации суперпользователя по API ключу"""
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API ключ ошибочен")
    result = await session.execute(select(User).where(User.api_key == api_key, User.is_superuser is True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Неправильный API ключ или имя суперюзера")
    return user
