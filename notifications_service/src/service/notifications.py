from dataclasses import dataclass
from typing import Any

from src.models.notifications import NotificationRecord
from src.crud.base import BaseMongoCRUD
from src.db.rabbitmq import rabbitmq_producer
from src.service.handlers.base import BaseHandler
from src.shemas.delivery import DeliveryDTO


import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class NotificationsService:
    producer: Any
    notification_records: BaseMongoCRUD = BaseMongoCRUD(NotificationRecord)

    async def get_history(self, filter_: dict, page_number: str, page_size: str) -> list[dict]:
        history_records = await self.notification_records.find(
            filter_=filter_, page_number=page_number, page_size=page_size
        )
        return history_records

    async def notification(self, delivery_data: DeliveryDTO) -> None:
        notification_data = await self.notification_records.find_one(
            filter_={"notification": delivery_data.notification}
        )

        if notification_data is None:
            raise ValueError(f"Уведомление {delivery_data.notification} не найдено в базе")

        handler_class = BaseHandler.get_handler(delivery_data.notification)
        handler = handler_class(producer=self.producer, data_store=notification_data)

        await handler.create_tasks(delivery_data)


def get_notifications_service() -> NotificationsService:
    return NotificationsService(
        producer=rabbitmq_producer,
    )
