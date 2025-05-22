import logging
from dataclasses import dataclass
from logging import config as logging_config
from typing import Dict, List

from config.elasticsearch import ElasticsearchClient
from elasticsearch.exceptions import ConnectionError
from elasticsearch.helpers import bulk
from state.state import State
from utils.backoff import backoff
from utils.logger import LOGGING_CONFIG

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


@dataclass
class ElasticsearchLoader:
    """Класс для загрузки данных в Elasticsearch."""

    client: ElasticsearchClient
    state: State
    index: str
    batch_size: int

    @backoff(ConnectionError)
    def bulk_load(self, batch: List[Dict], last_mod: str) -> None:
        """Метод для выполнения массовой загрузки."""

        logger.info("Началась массовая загрузка для индекса: %s", self.index)
        bulk(
            client=self.client.connection,
            actions=batch,
            index=self.index,
            chunk_size=self.batch_size,
        )
        logger.info("Массовая загрузка для индекса %s завершена успешно", self.index)
        self.state.set_state(self.index, last_mod)
        logger.info("Состояние индекса %s обновлено на: %s", self.index, last_mod)
