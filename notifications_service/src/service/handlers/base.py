import abc
from typing import ClassVar, Type, TypeVar

from src.models.dto import AbstractDTO
from src.shemas.delivery import DeliveryDTO

HandlerT = TypeVar("HandlerT", bound="BaseHandler")


class BaseHandler(abc.ABC):
    _handlers: ClassVar[dict[str, Type["BaseHandler"]]] = {}
    notification: ClassVar[str]

    def __init__(self, producer, data_store):
        self.producer = producer
        self.data_store = data_store

    def __init_subclass__(cls, **kwargs) -> None:
        """Автоматически регистрируем подклассы с их notification."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "notification") and cls.notification:
            cls._handlers[cls.notification] = cls
        else:
            raise ValueError(f"Подкласс {cls.__name__} должен иметь атрибут notification")

    @abc.abstractmethod
    async def create_tasks(self, delivery_data: DeliveryDTO) -> None:
        raise NotImplementedError

    @classmethod
    def get_handler(cls, notification: str) -> Type["BaseHandler"]:
        """Получаем обработчик по notification."""
        handler = cls._handlers.get(notification)
        if not handler:
            raise ValueError(f"Обработчик для notification_id {notification} не найден")
        return handler

    async def _publish_message(self, message: AbstractDTO, queue_name: str, queue_durable: bool = True) -> None:
        """
        Публикует сообщение в очередь RabbitMQ.
        """
        try:
            await self.producer.publish(message=message, queue_name=queue_name, queue_durable=queue_durable)
        except Exception as e:
            raise e
