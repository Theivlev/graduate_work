from faststream.rabbit import RabbitBroker
from src.core.config import rabbitmq_settings
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info(f'Данные для подключения {rabbitmq_settings.dsn}')
broker = RabbitBroker(rabbitmq_settings.dsn)
