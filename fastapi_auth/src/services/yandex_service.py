import uuid
from dataclasses import dataclass

import aiohttp
from fastapi.responses import RedirectResponse
from fastapi_users.exceptions import UserNotExists
from src.core.config import redis_settings, yandex_settings
from src.core.user_core import UserManager, auth_backend, get_user_manager, refresh_auth_backend
from src.db.redis_cache import RedisClientFactory
from src.schemas.user_schema import UserCreate

from fastapi import Depends


def get_yandex_service(user_manager: UserManager = Depends(get_user_manager)) -> "YandexService":
    """Функция для получения сервиса яндекса"""
    return YandexService(user_manager)


@dataclass
class YandexService:
    """Сервис для работы с Яндексом."""

    user_manager: UserManager

    async def get_yandex_code(self, url, device_id: str = None, device_name: str = "Yandex Device") -> str:
        """Получение данных для ссылки редиректа в Яндекс"""
        if device_name:
            url += f"&device_name={device_name}"
            if not device_id:
                device_id = str(uuid.uuid4())
            url += f"&device_id={device_id}"
        redis_client = await RedisClientFactory.create(redis_settings.dsn)
        await redis_client.set(f"yandex_device:{device_name}", device_id)
        return RedirectResponse(url, status_code=307)

    async def get_yandex_token(self, code: str, device_id: str = None, device_name: str = "Yandex Device") -> str:
        """Получение на сайте Яндекса access_token"""
        if not device_id:
            redis_client = await RedisClientFactory.create(redis_settings.dsn)
            device_id = await redis_client.get(f"yandex_device:{device_name}")
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": yandex_settings.client_id,
            "client_secret": yandex_settings.client_secret,
            "device_id": device_id.decode("ascii"),
            "device_name": device_name,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(yandex_settings.token_url, data=data) as response:
                token_response = await response.json()
                return token_response.get("access_token"), device_id

    async def get_yandex_user_info(self, access_token: str) -> dict:
        """Получение данных на сайте Яндекса пользователя"""
        user_info_headers = {"Authorization": f"OAuth {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(yandex_settings.user_info_url, headers=user_info_headers) as response:
                return await response.json()

    async def revoke_yandex_token(self, access_token: str) -> dict:
        """Получение статуса разлогинивания на сайте Яндекса пользователя"""
        data = {
            "access_token": access_token,
            "client_id": yandex_settings.client_id,
            "client_secret": yandex_settings.client_secret,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(yandex_settings.revoke_token_url, data=data) as response:
                return await response.json()

    async def logined_yandex_user(self, user, device_id: str, device_name: str) -> dict:
        """Генерация токенов для пользователя"""
        access_token = await auth_backend.get_strategy().write_token(user)
        refresh_token = await refresh_auth_backend.get_strategy().write_token(user)
        redis_client = await RedisClientFactory.create(redis_settings.dsn)
        await redis_client.set(f"access_token:{user.id}", access_token)
        await redis_client.set(f"refresh_token:{user.id}", refresh_token)
        await redis_client.set(f"yandex_device:{device_name}", device_id)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def login_yandex_user(self, code: str, device_id: str = None, device_name: str = "Yandex Device") -> dict:
        """Авторизация пользователя по данным Яндекса."""
        access_token, device_id = await self.get_yandex_token(code, device_id, device_name)
        user_info = await self.get_yandex_user_info(access_token)
        email = user_info["default_email"]
        try:
            user = await self.user_manager.get_by_email(email)
        except UserNotExists:
            password_hash = self.user_manager.password_helper.hash(email)
            user_data = UserCreate(
                email=email,
                password=password_hash,
                is_active=True,
                is_superuser=False,
                is_verified=True,
            )
            user = await self.user_manager.create(user_data)
        tokens = await self.logined_yandex_user(user, device_id, device_name)
        return {"message": "Успешная авторизация через Яндекс", "email": email, **tokens}

    async def logout_yandex_user(
        self, code: str, user, device_id: str = None, device_name: str = "Yandex Device"
    ) -> dict:
        """Разлогинивание пользователя по данным Яндекса."""
        access_token, device_id = await self.get_yandex_token(code, device_id, device_name)
        logout_response = await self.revoke_yandex_token(access_token)
        # redis_client = await RedisClientFactory.create(redis_settings.dsn)
        # await redis_client.delete(f"access_token:{user.id}")
        # await redis_client.delete(f"refresh_token:{user.id}")
        # await redis_client.delete(f"yandex_device:{device_name}", device_id)
        return {"status": "Tokens revoked", **logout_response}
