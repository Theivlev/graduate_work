import logging
import time
from contextlib import closing
from datetime import datetime
from logging import config as logging_config

from config import ElasticsearchClient, PostgresClient, RedisClient
from config.settings import Settings
from elasticsearch.helpers import BulkIndexError
from etl.extract.data_extract import PostgresExtractor
from etl.load.data_loader import ElasticsearchLoader
from etl.transform.data_transform import DataTransform
from models.etl import ETL
from state.redis_storage import RedisStorage
from state.state import State
from utils.logger import LOGGING_CONFIG

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


def etl(etl: "ETL", settings: Settings) -> None:
    """ETL процесс для конкретного маппера."""

    logger.info("%s ETL начат", etl.index.value)

    with closing(ElasticsearchClient(settings.elasticsearch_dsn)) as elasticsearch_client, closing(
        PostgresClient(settings.postgres_dsn)
    ) as postgres_client, closing(RedisClient(settings.redis_dsn)) as redis_client:
        state = State(storage=RedisStorage(redis_client=redis_client))

        if not state.get_state(key=str(etl.index.value)):
            state.set_state(key=str(etl.index.value), value=str(datetime.min))

        extractor = PostgresExtractor(
            postgres_client=postgres_client,
            state=state,
            etl=etl,
            batch_size=settings.batch_size,
            query=etl.query,
        )

        transformer = DataTransform(model=etl.model)

        loader = ElasticsearchLoader(
            client=elasticsearch_client, state=state, index=etl.index.value, batch_size=settings.batch_size
        )

        while True:
            for data, last_modified in extractor.extract():
                if data:
                    transformed_data = transformer.data_transform(data)
                    try:
                        loader.bulk_load(transformed_data, last_modified)
                    except BulkIndexError as e:
                        logger.error("Ошибка при индексации в Elasticsearch: %s", e)
                        for error in e.errors:
                            logger.error(
                                "Ошибка для документа ID=%s: %s", error["index"]["_id"], error["index"]["error"]
                            )

            logger.info("%s ETL завершён, засыпаем на %s с", etl.index.value, settings.timeout)

            time.sleep(settings.timeout)
