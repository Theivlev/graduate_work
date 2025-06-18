from typing import ClassVar

from src.service.handlers.base import BaseHandler
from src.shemas.delivery import DeliveryDTO
from src.shemas.message_release import MessageEpisodeReleaseDTO


class EpisodeReleaseHandler(BaseHandler):
    notification: ClassVar[str] = "episode_release"

    async def create_tasks(self, delivery_data: DeliveryDTO) -> None:
        user_data: dict = delivery_data.data_store
        message = MessageEpisodeReleaseDTO.create(user_data)

        await self._publish_message(message, message.notification_queue)
