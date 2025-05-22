import contextlib
import logging

from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from pydantic import EmailStr

from src.core.config import auth_settings
from src.core.user_core import get_user_db, get_user_manager
from src.db.postgres import get_async_session
from src.schemas.user_schema import UserCreate
from src.core.user_core import get_user_manager

logger = logging.getLogger(__name__)


get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(email: EmailStr, password: str, is_superuser: bool = False):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(UserCreate(email=email, password=password, is_superuser=is_superuser))
    except UserAlreadyExists:
        pass

async def create_first_superuser():
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                try:
                    user = await user_manager.get_by_email(auth_settings.first_superuser_email)
                except UserNotExists:
                    user = await user_manager.create(
                        UserCreate(
                            email=auth_settings.first_superuser_email,
                            password=auth_settings.first_superuser_password,
                            is_superuser=True,
                            is_verified=True,
                        )
                    )
                    logger.info(f"Superuser {auth_settings.first_superuser_email} created")
                else:
                    logger.info(f"Superuser {auth_settings.first_superuser_email} already exists")