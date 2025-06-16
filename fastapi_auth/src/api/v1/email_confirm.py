import jwt
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import project_settings, redis_settings, ws_settings
from src.db.postgres import get_async_session
from src.db.rabbitmq import rabbitmq_producer
from src.db.redis_cache import RedisClientFactory
from src.models.user import User
from src.schemas.rabbit_schema import WsMessage

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/s/{short_id}")
async def confirm_email(short_id: str, session: AsyncSession = Depends(get_async_session)):
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

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not user.is_verified:
        user.is_verified = True
        message = WsMessage(email=str(user.email), fullname=f"{user.name} {user.surname}", event_type="user_verified")
        print(message)
        await rabbitmq_producer.publish(
            message.json(), exchange_name=ws_settings.ws_exchange, routing_key=ws_settings.ws_routing_key
        )
        await session.commit()

    await redis.delete(f"email_confirm:{short_id}")

    return RedirectResponse(redirect_url)
