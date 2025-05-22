import aio_pika
from aio_pika.exceptions import AMQPConnectionError
from src.core.config import rabbit_settings
from src.models.dto import AbstractDTO
from src.utils.backoff import backoff


class RabbitMQManager:
    """Класс для работы с RabbitMQ."""

    connection = None
    channel = None

    def __init__(
        self,
        user: str = rabbit_settings.user,
        password: str = rabbit_settings.password,
        port: int = rabbit_settings.port,
        host: str = rabbit_settings.host,
        vhost: str = "/",
    ):
        """Инициализация класса."""
        self.dsn = f"amqp://{user}:{password}@{host}:{port}/{vhost}"

    @backoff(AMQPConnectionError)
    async def setup(self) -> None:
        """Подключение к RabbitMQ."""
        self.connection = await aio_pika.connect_robust(self.dsn)
        self.channel = await self.connection.channel()

    async def close(self) -> None:
        """Закрытие соединения с RabbitMQ."""
        if self.connection:
            await self.connection.close()

    async def publish(self, message: str | AbstractDTO, queue_name: str, queue_durable: bool = True) -> None:
        """Отправка сообщения в очередь."""
        await self.channel.declare_queue(queue_name, durable=queue_durable)
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=message.encode("utf-8"), delivery_mode=2 if queue_durable else 1),
            routing_key=queue_name,
        )


rabbitmq_producer = RabbitMQManager()
