import secrets
from contextlib import asynccontextmanager

from sqlalchemy import select
from src.core.config import project_settings
from src.db.postgres import get_async_session
from src.models.user_model import User


@asynccontextmanager
async def get_db_session():
    async for session in get_async_session():
        yield session


async def create_superuser():
    """Создает суперпользователя при старте приложения"""
    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.name == project_settings.superuser_name))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            return existing_user
        api_key = secrets.token_urlsafe(32) if project_settings.superuser_api_key else None
        superuser = User(
            name=project_settings.superuser_name,
            role="admin",
            is_superuser=True,
            api_key=api_key,
        )
        session.add(superuser)
        await session.commit()
        return superuser
