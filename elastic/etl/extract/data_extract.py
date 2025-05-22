import logging
from dataclasses import dataclass
from logging import config as logging_config
from typing import Callable

from config.postgres import PostgresClient
from etl.extract.query import Query
from models.etl import ETL
from psycopg.errors import ConnectionFailure
from psycopg.sql import SQL
from state.state import State
from utils.backoff import backoff
from utils.logger import LOGGING_CONFIG

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


@dataclass
class PostgresExtractor:
    postgres_client: PostgresClient
    state: State
    etl: ETL
    batch_size: int
    query: Callable[[str], SQL]

    @backoff(ConnectionFailure)
    def check_modified(self, prev_mod: str) -> str | None:
        """Проверяет, были ли изменены данные в таблице."""
        logger.info("Проверка изменений в таблице %s с предыдущей меткой времени %s", self.etl.table.value, prev_mod)

        self.postgres_client.cursor.execute(Query.check_modified(self.etl.table.value, prev_mod))

        result = self.postgres_client.cursor.fetchone()

        if result is None:
            logger.warning("Результат запроса пустой для таблицы %s", self.etl.table.value)
            return None

        last_modified = result["last_modified"]
        logger.info("Последнее изменение в таблице %s: %s", self.etl.table.value, last_modified)
        return last_modified

    @backoff(ConnectionFailure)
    def extract(self):
        """Извлекает данные о фильмах из Postgres."""

        prev_mod = self.state.get_state(self.etl.index.value)

        if last_modified := self.check_modified(prev_mod):
            logger.info("Извлечение новых данных для %s", self.etl.index.value)

            self.postgres_client.cursor.execute(self.query(prev_mod))

            while data := self.postgres_client.cursor.fetchmany(size=self.batch_size):
                yield data, str(last_modified)
