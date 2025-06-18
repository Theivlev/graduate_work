import base64
import hashlib
import random
import string
from dataclasses import dataclass

import aiohttp
from fastapi.responses import RedirectResponse
from fastapi_users.exceptions import UserNotExists
from src.core.config import redis_settings, vk_settings
from src.core.user_core import UserManager, auth_backend, get_user_manager, refresh_auth_backend
from src.db.redis_cache import RedisClientFactory
from src.schemas.user_schema import UserCreate

from fastapi import Depends, HTTPException


def get_vk_service(user_manager: UserManager = Depends(get_user_manager)) -> "VkService":
    """Функция для получения сервиса ВК"""
    return VkService(user_manager)


@dataclass
class VkService:
    """Сервис для работы с ВК."""

    user_manager: UserManager
    code_verifier_length: int = 128
    state_length: int = 32
    redis_ttl: int = 600

    async def get_random_characters(self, length: int) -> str:
        """Генерирует случайную строку состояния нужной длины."""
        characters = string.ascii_letters + string.digits + "_-"
        return "".join(random.choice(characters) for _ in range(length))

    async def generate_code_challenge(self, code_verifier: str) -> str:
        """Преобразует code_verifier в code_challenge с использованием метода S256."""
        if isinstance(code_verifier, bytes):
            code_verifier_bytes = code_verifier
        else:
            code_verifier_bytes = code_verifier.encode("ascii")
        sha256_hash = hashlib.sha256(code_verifier_bytes).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_hash).decode("ascii")
        return code_challenge.rstrip("=")

    async def get_vk_code(self, url) -> str:
        """Получение данных для ссылки редиректа в ВК"""
        redis = await RedisClientFactory.create(redis_settings.dsn)
        state = await redis.get("state")
        if not state:
            state = await self.get_random_characters(self.state_length)
            await redis.set("state", state, ex=self.redis_ttl)
        else:
            state = state.decode("ascii")
        code_verifier = await redis.get("code_verifier")
        if not code_verifier:
            code_verifier = await self.get_random_characters(self.code_verifier_length)
            await redis.set("code_verifier", code_verifier, ex=self.redis_ttl)
        else:
            code_verifier.decode("ascii")
        code_challenge = await self.generate_code_challenge(code_verifier)
        query = (
            f"?response_type=code"
            f"&client_id={vk_settings.client_id}"
            f"&redirect_uri={url}"
            f"&state={state}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method={vk_settings.code_challenge_method}"
            f"&scope=email"
        )
        return RedirectResponse(f"{vk_settings.auth_url}{query}", status_code=307)

    async def get_vk_token(self, code: str, device_id: str, state: str, redirect_uri: str) -> str:
        """Получение на сайте ВК access_token"""
        redis = await RedisClientFactory.create(redis_settings.dsn)
        state_redis = await redis.get("state")
        if not state_redis or state != state_redis.decode("ascii"):
            raise HTTPException(status_code=404, detail="Param: state incorrect")
        code_verifier = await redis.get("code_verifier")
        if not code_verifier:
            raise HTTPException(status_code=404, detail="Param: code_verifier is not found in redis")
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": vk_settings.client_id,
            "client_secret": vk_settings.client_secret,
            "code_verifier": code_verifier.decode("ascii"),
            "device_id": device_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(vk_settings.token_url, data=data) as response:
                token_response = await response.json()
                return token_response.get("access_token")

    async def get_vk_user_info(self, access_token: str) -> dict:
        """Получение данных на сайте ВК пользователя"""
        data = {"client_id": vk_settings.client_id, "access_token": access_token}
        async with aiohttp.ClientSession() as session:
            async with session.post(vk_settings.user_info_url, data=data) as response:
                return await response.json()

    async def revoke_vk_token(self, access_token: str) -> dict:
        """Получение статуса разлогинивания на сайте ВК пользователя"""
        data = {
            "client_id": vk_settings.client_id,
            "access_token": access_token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(vk_settings.logout_url, data=data) as response:
                return await response.json()

    async def logined_vk_user(self, user) -> dict:
        """Генерация токенов для пользователя"""
        access_token = await auth_backend.get_strategy().write_token(user)
        refresh_token = await refresh_auth_backend.get_strategy().write_token(user)
        redis = await RedisClientFactory.create(redis_settings.dsn)
        await redis.set(f"access_token:{user.id}", access_token)
        await redis.set(f"refresh_token:{user.id}", refresh_token)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def login_vk_user(self, code: str, device_id: str, state: str, redirect_uri: str) -> dict:
        """Авторизация пользователя по данным ВК."""
        access_token = await self.get_vk_token(code, device_id, state, redirect_uri)
        user_info = await self.get_vk_user_info(access_token)
        email = user_info["user"]["email"]
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
        tokens = await self.logined_vk_user(user)
        return {"message": "Успешная авторизация через ВК", "email": email, **tokens}

    async def logout_vk_user(self, code: str, user, device_id: str, state: str, redirect_uri: str) -> dict:
        """Разлогинивание пользователя по данным ВК."""
        access_token = await self.get_vk_token(code, device_id, state, redirect_uri)
        logout_response = await self.revoke_vk_token(access_token)
        # redis = await RedisClientFactory.create(redis_settings.dsn)
        # await redis.delete(f"access_token:{user.id}")
        # await redis.delete(f"refresh_token:{user.id}")
        return {"status": "Tokens revoked", **logout_response}
