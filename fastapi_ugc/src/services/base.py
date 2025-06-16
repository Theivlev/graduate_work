import logging
from datetime import datetime
from typing import Generic, List, Type
from uuid import UUID

from broker.kafka import kafka_producer
from src.core.config import kafka_settings
from src.crud.base import BaseMongoCRUD, ModelType
from src.shemas.broker import KafkaSendMessage

logger = logging.getLogger(__name__)


class BaseService(Generic[ModelType]):  # type: ignore[misc]
    """Базовый класс сервиса."""

    def __init__(self, model: Type[ModelType]):
        """Инициализация сервиса."""

        self.crud = BaseMongoCRUD(model=model)

    async def create(self, data: dict) -> ModelType:
        """Создает нового объекта в базе данных."""
        result = await self.crud.create(data)
        await self.send_kafka("create", data.get("user_id"), data.get("movie_id"))
        return result

    async def get(self, id_: str) -> ModelType | None:
        """Получить объект по ID."""
        return await self.crud.get(id_)

    async def find(self, filter_: dict, page_number: int = 0, page_size: int = 10) -> List[ModelType]:
        """Ищет объекты в базе данных с пагинацией."""
        result = await self.crud.find(filter_, page_number, page_size)
        return result

    async def update(self, id_: str, data: dict) -> ModelType | None:
        """Обновляет объект в базе данных."""
        result = await self.crud.update(id_, data)
        await self.send_kafka("update", data.get("user_id"), data.get("movie_id"))
        return result

    async def delete(self, id_: str, user_id: str | None) -> bool:
        """Удаляет объект из базы данных."""
        result = await self.crud.delete(id_)
        await self.send_kafka("delete", user_id, id_)
        return result

    async def send_kafka(
        self, action: str, user_id: str | UUID | None, movie_id: str | UUID | None, data: str = ""
    ) -> None:
        """Отправляет сообщение в Kafka."""
        if user_id and movie_id:
            try:
                await kafka_producer.send_and_wait(
                    topic=kafka_settings.topic,
                    value=str.encode(
                        KafkaSendMessage(
                            user_id=user_id if isinstance(user_id, UUID) else UUID(user_id),
                            movie_id=movie_id if isinstance(movie_id, UUID) else UUID(movie_id),
                            action=f"{action} {self.crud.model.get_name()}",
                            event_data=data,
                            event_time=datetime.now(),
                        ).model_dump_json()
                    ),
                )
            except Exception as e:
                logger.error(f"Error while sending kafka message: {e}")
