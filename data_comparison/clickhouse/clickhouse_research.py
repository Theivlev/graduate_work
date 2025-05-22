import logging
import random
from datetime import datetime
from time import time
from uuid import uuid4

from clickhouse_connect import get_client
from faker import Faker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

fake: Faker = Faker()

logger.info("Генерация кэша имен, фамилий и email...")
NAMES = [fake.first_name() for _ in range(1000)]
SURNAMES = [fake.last_name() for _ in range(1000)]
DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "example.com"]


def generate_email(name, surname):
    return f"{name.lower()}.{surname.lower()}@{random.choice(DOMAINS)}"


logger.info("Подключение к ClickHouse...")
client = get_client(host="clickhouse", port=8123)
logger.info("Успешно подключено к ClickHouse")

BATCH_SIZE: int = 10000
BATCHES: int = 1000
TOTAL: float = BATCH_SIZE * BATCHES


logger.info("Создание таблицы user_data (если не существует)...")
client.command(
    """
    CREATE TABLE IF NOT EXISTS user_data
    (
        user_id UUID,
        name String,
        surname String,
        email String,
        created_at DateTime
    )
    ENGINE = MergeTree()
    ORDER BY (user_id, created_at)
    """
)
logger.info("Таблица user_data готова")


def insert_data():
    """Генерация и вставка данных в таблицу."""
    logger.info("Начало вставки данных...")
    start_time: float = time()

    for batch in range(BATCHES):
        data = [
            (
                str(uuid4()),
                random.choice(NAMES),
                random.choice(SURNAMES),
                generate_email(random.choice(NAMES), random.choice(SURNAMES)),
                datetime.now(),
            )
            for _ in range(BATCH_SIZE)
        ]
        client.insert("user_data", data, column_names=["user_id", "name", "surname", "email", "created_at"])
        if (batch + 1) % 100 == 0:
            logger.info(f"Обработано {batch + 1}/{BATCHES} батчей ({(batch + 1) * BATCH_SIZE:,} записей)")

    insertion_time: float = time() - start_time
    insertion_speed: float = round(TOTAL / insertion_time, 2)

    logger.info(f"Вставка завершена. Скорость вставки: {insertion_speed:,} записей/сек")


def read_data():
    """Чтение данных из таблицы."""
    logger.info("Начало чтения данных...")
    start_time: float = time()

    query = "SELECT user_id, name, surname, email, created_at FROM user_data"
    result = client.query(query)

    logger.info(f"Прочитано записей: {len(result.result_rows):,}")
    reading_time: float = time() - start_time
    reading_speed: float = round(TOTAL / reading_time, 2)
    logger.info(f"Чтение завершено. Скорость чтения: {reading_speed:,} записей/сек")


if __name__ == "__main__":
    logger.info("Запуск скрипта...")
    insert_data()
    read_data()
    logger.info("Скрипт успешно завершен")
