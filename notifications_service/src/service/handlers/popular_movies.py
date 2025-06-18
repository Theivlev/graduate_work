from typing import ClassVar

from src.service.handlers.base import BaseHandler
from src.shemas.delivery import DeliveryDTO
from src.shemas.message_popular import MessagePopularMoviesDTO


class PopularMoviesHandler(BaseHandler):
    notification: ClassVar[str] = "popular_movies"

    async def create_tasks(self, delivery_data: DeliveryDTO) -> None:
        """
        Создает задачи для отправки уведомлений о популярных фильмах в очередь RabbitMQ.
        """
        user_data: dict = delivery_data.data_store
        message = MessagePopularMoviesDTO.create(user_data)

        await self._publish_message(message, message.notification_queue)
