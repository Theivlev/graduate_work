import logging
from logging import config as logging_config

import psycopg
from psycopg.errors import ConnectionFailure
from psycopg.rows import dict_row
from pydantic import PostgresDsn
from utils.backoff import backoff
from utils.logger import LOGGING_CONFIG

from .base import BaseConfig

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


class PostgresClient(BaseConfig):
    """Класс клиента для работы с PostgreSQL."""

    def __init__(self, dsn: PostgresDsn, connect=None):
        super().__init__(dsn, connect)
        self.cursor = self.connection.cursor(row_factory=dict_row)

    @backoff(ConnectionFailure)
    def reconnect(self):
        """Подключение к PostgreSQL."""
        logger.info("Попытка подключения к PostgreSQL с dsn: %s", self.dsn)
        self.connect = psycopg.connect(str(self.dsn))
        self.cursor = self.connection.cursor(row_factory=dict_row)
        return self.connection
