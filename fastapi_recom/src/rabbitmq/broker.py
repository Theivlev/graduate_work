from faststream.rabbit import RabbitBroker
from core.config import rabbitmq_settings


broker = RabbitBroker(rabbitmq_settings.model_config)
