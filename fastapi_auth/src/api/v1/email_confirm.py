from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import get_async_session
from src.models.user import User
from src.core.config import project_settings, redis_settings
from src.db.redis_cache import RedisClientFactory
import jwt

router = APIRouter()

@router.get("/s/{short_id}")
async def confirm_email(
    short_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    redis = await RedisClientFactory.create(redis_settings.dsn)
    token = await redis.get(f"email_confirm:{short_id}")
    if not token:
        raise HTTPException(status_code=404, detail="Ссылка недействительна или устарела")
    try:
        payload = jwt.decode(token, project_settings.secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=404, detail="Срок действия ссылки истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=404, detail="Некорректная ссылка")

    user_id = payload["user_id"]
    redirect_url = payload["redirectUrl"]
    print(f"user_id: {user_id}, redirect_url: {redirect_url}")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not user.is_verified:
        user.is_verified = True
        await session.commit()

    await redis.delete(f"email_confirm:{short_id}")

    return RedirectResponse(redirect_url)