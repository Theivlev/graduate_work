from faststream.rabbit import RabbitBroker
from core.config import rabbit_settings


broker = RabbitBroker(rabbit_settings.model_config)
