from typing import ClassVar

from src.service.handlers.base import BaseHandler
from src.shemas.delivery import DeliveryDTO
from src.shemas.message_registered import MessageRegisteredDTO


class UserRegisteredHandler(BaseHandler):
    notification: ClassVar[str] = "user_registered"

    async def create_tasks(self, delivery_data: DeliveryDTO) -> None:
        user_data: dict = delivery_data.data_store
        message = MessageRegisteredDTO.create(user_data)

        await self._publish_message(message, message.notification_queue)
