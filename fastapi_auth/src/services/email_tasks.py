
import jwt
import base64
import hashlib
from datetime import datetime, timedelta, timezone

from src.db.rabbitmq import rabbitmq_producer
from src.core.config import project_settings, redis_settings, mail_queue_settings
from src.db.redis_cache import RedisClientFactory
from src.schemas.email import EmailMessage


def generate_confirmation_token(user_id: str, redirect_url: str, secret: str, expires_in: int = 3600):
    payload = {
        "user_id": user_id,
        "redirectUrl": redirect_url,
        "exp": (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).timestamp()
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def make_short_id(token: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(token.encode()).digest())[:8].decode()


async def send_confirmation_email_task(user):
    token = generate_confirmation_token(
        user_id=str(user.id),
        redirect_url=mail_queue_settings.redirect_url,
        secret=project_settings.secret
    )
    short_id = make_short_id(token)
    confirmation_link = f"{mail_queue_settings.url_confirm}{short_id}"

    redis = await RedisClientFactory.create(redis_settings.dsn)
    await redis.set(f"email_confirm:{short_id}", token, ex=3600)

    message = EmailMessage(
        user_id=str(user.id),
        subject="Подтвердите ваш email",
        template="registration.html",
        confirmation_link=confirmation_link
    )
    await rabbitmq_producer.publish(
        message.json(),
        exchange_name=mail_queue_settings.mail_exchange,
        routing_key=mail_queue_settings.mail_routing_key,
    )