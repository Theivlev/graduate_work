import logging
from logging import config as logging_config
from threading import Thread

from config.settings import settings
from etl.etl import etl
from etl.extract.query import Query
from models.etl import ETL, ETLManager, Indexes, Tables
from models.genre import GenreDTO
from models.movie import MovieDTO
from models.person import PersonInfoDTO
from utils.logger import LOGGING_CONFIG

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


def main():
    etl_manager = ETLManager(settings, etl_function=etl)

    etl_configs = [
        ETL(Indexes.MOVIES, Tables.FILM_WORK, MovieDTO, Query.get_films_query),
        ETL(Indexes.PERSONS, Tables.PERSON, PersonInfoDTO, Query.get_persons_query),
        ETL(Indexes.GENRES, Tables.GENRE, GenreDTO, Query.get_genres_query),
    ]

    threads: list[Thread] = []
    for config in etl_configs:
        thread = Thread(target=etl_manager.run_etl, args=(config,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logger.info("✅ Все ETL процессы запущены в отдельных потоках!")


if __name__ == "__main__":
    main()
