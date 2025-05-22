from datetime import datetime
from typing import Annotated, AsyncGenerator, Union
from uuid import UUID

from fastapi_users import BaseUserManager, FastAPIUsers, InvalidPasswordException, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import auth_settings, project_settings, redis_settings
from src.db.postgres import get_async_session
from src.db.redis_cache import RedisClientFactory
from src.models.auth_history import AuthHistory
from src.models.user import User
from src.schemas.user_schema import UserCreate
from src.utils.detect_device import detect_device_type
from src.services.email_tasks import send_confirmation_email_task

from fastapi import Depends, Request


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """Получает базу данных пользователей SQLAlchemy."""
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl="/auth/v1/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """Возвращает стратегию JWT для аутентификации."""
    return JWTStrategy(secret=auth_settings.secret, lifetime_seconds=auth_settings.jwt_lifetime_seconds)


def get_refresh_jwt_strategy() -> JWTStrategy:
    """Возвращает стратегию JWT для обновления токена."""
    return JWTStrategy(secret=project_settings.secret, lifetime_seconds=project_settings.jwt_refresh_lifetime_seconds)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

refresh_auth_backend = AuthenticationBackend(
    name="refresh_jwt",
    transport=bearer_transport,
    get_strategy=get_refresh_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """Менеджер пользователей, наследующий UUIDIDMixin и BaseUserManager."""

    async def validate_password(self, password: str, user: Union[UserCreate, User]) -> None:
        """Валидирует пароль пользователя."""
        if len(password) < project_settings.min_password_length:
            raise InvalidPasswordException(
                reason=f"Пароль должен содержать не менее {project_settings.min_password_length} символов"
            )
        if user.email in password:
            raise InvalidPasswordException(reason="Пароль не может содержать ваш email")

    async def on_after_register(self, user: User, request: Request | None = None) -> None:
        """Выполняется после регистрации пользователя."""
        if user.is_superuser:
          return
        await send_confirmation_email_task(user)

    async def on_after_login(self, user: User, request: Request | None = None, response=None) -> None:
        """Выполняется после входа пользователя в систему."""
        redis = await RedisClientFactory.create(redis_settings.dsn)
        refresh_token = await refresh_auth_backend.get_strategy().write_token(user)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        user_agent = request.headers.get("User-Agent")
        async for session in get_async_session():
            auth_entry = AuthHistory(
                user_id=user.id,
                user_agent=user_agent,
                user_device_type=detect_device_type(user_agent),
                timestamp=datetime.now(),
            )
            session.add(auth_entry)
            await session.commit()

        await redis.set(f"refresh_token:{user.id}", refresh_token)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Получает менеджер пользователей."""
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend, refresh_auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
