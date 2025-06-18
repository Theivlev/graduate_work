import logging
from logging import config as logging_config

from redis import Redis
from redis.exceptions import ConnectionError
from redis.typing import EncodableT, KeyT
from utils.backoff import backoff
from utils.logger import LOGGING_CONFIG

from .base import BaseConfig

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


class RedisClient(BaseConfig):
    """Конфигурация и операции клиента Redis."""

    @backoff(ConnectionError)
    def reconnect(self) -> Redis:
        """Переподключение к Redis, если соединение отсутствует."""
        logger.info("Попытка подключения к Redis...")
        redis_client = Redis(host=self.dsn.host, port=int(self.dsn.port), db=self.dsn.path[1:])
        logger.info("Соединение с Redis выполнено успешно!")
        return redis_client

    @backoff(ConnectionError)
    def set(self, key: KeyT, value: EncodableT, *args, **kwargs) -> None:
        """Устанавливает значение в Redis."""
        logger.debug(f"Устанавливаем ключ: {key} со значением: {value}")
        self.connection.set(key, value, *args, **kwargs)
        logger.info(f"Ключ {key} установлен успешно.")

    @backoff(ConnectionError)
    def get(self, key: KeyT) -> bytes | None:
        """Получает значение из Redis."""
        logger.debug(f"Получаем значение для ключа: {key}")
        value = self.connection.get(key)
        logger.info(f"Получено значение для ключа {key}: {value}")
        return value
