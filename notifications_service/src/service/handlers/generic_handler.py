from typing import ClassVar

from src.service.handlers.base import BaseHandler
from src.shemas.delivery import DeliveryDTO
from src.shemas.message_generic import MessageGenericDTO


class GenericHandler(BaseHandler):
    notification: ClassVar[str] = "generic"

    async def create_tasks(self, delivery_data: DeliveryDTO) -> None:
        """
        Создает задачу для отправки общего уведомления в очередь RabbitMQ.
        """
        user_data: dict = delivery_data.data_store
        message = MessageGenericDTO.create(user_data)

        await self._publish_message(message, message.notification_queue)
