from faststream.rabbit import RabbitBroker
from src.core.config import rabbitmq_settings

broker = RabbitBroker(rabbitmq_settings.dsn)
