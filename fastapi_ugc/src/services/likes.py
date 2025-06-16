import logging
from datetime import datetime
from uuid import UUID

import aio_pika

from broker.rabbit import get_rabbitmq_channel
from src.crud.base import ModelType
from src.models.like import UserLikes
from src.services.base import BaseService
from src.shemas.broker import RabbitSendMessage

logger = logging.getLogger(__name__)


class LikesService(BaseService):
    """Сервис для работы с коллекцией 'user_likes'."""

    async def create(self, data: dict) -> ModelType:
        """Создает нового объекта в базе данных."""
        result = await self.crud.create(data)
        await self.send_create_rabbitmq(data.get("user_id"), data.get("movie_id"), str(data.get("rating")))
        await self.send_kafka("create", data.get("user_id"), data.get("movie_id"), str(data.get("rating")))
        return result

    async def update(self, id_: str, data: dict) -> ModelType | None:
        """Обновляет объект в базе данных."""
        result = await self.crud.update(id_, data)
        await self.send_kafka("update", data.get("user_id"), data.get("movie_id"), str(data.get("rating")))
        return result

    @staticmethod
    async def send_create_rabbitmq(user_id: str | UUID | None, movie_id: str | UUID | None, data: str = "") -> None:
        channel = get_rabbitmq_channel()
        if user_id and movie_id:
            try:
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=RabbitSendMessage(
                            user_id=str(user_id) if isinstance(user_id, UUID) else user_id,
                            movie_id=str(movie_id) if isinstance(movie_id, UUID) else movie_id,
                            action={"type": "rate", "data": data},
                            event_data=data,
                            event_time=datetime.now(),
                        )
                        .model_dump_json()
                        .encode()
                    ),
                    routing_key="actions",
                )
            except Exception as e:
                logger.error(f"Error while sending rabbitmq message: {e}")


async def get_likes_service() -> BaseService:
    """Возвращает экземпляр CRUD-сервиса для работы с коллекцией 'user_likes'."""
    return LikesService(model=UserLikes)
