import logging
import random
from datetime import datetime
from time import time
from uuid import uuid4

from faker import Faker
from pydantic import BaseModel, Field
from vertica_python import Connection, connect
from vertica_python.vertica.cursor import Cursor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.info("Генерация кэша имен, фамилий и email...")

fake: Faker = Faker()

NAMES = [fake.first_name() for _ in range(1000)]
SURNAMES = [fake.last_name() for _ in range(1000)]
DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "example.com"]


def generate_email(name, surname):
    return f"{name.lower()}.{surname.lower()}@{random.choice(DOMAINS)}"


BATCH_SIZE: int = 10000
BATCHES: int = 1000
TOTAL: float = BATCH_SIZE * BATCHES


class ConnectionInfo(BaseModel):
    host: str = Field(default="vertica", description="Database host")
    port: int = Field(default=5433, description="Database port")
    user: str = Field(default="dbadmin", description="Database username")
    password: str = Field(default="", description="Database password")
    database: str = Field(default="docker", description="Database name")
    autocommit: bool = Field(default=True, description="Autocommit mode")


connection_info: ConnectionInfo = ConnectionInfo()


logger.info(f"Параметры подключения: {connection_info}")
connection: Connection = connect(**connection_info.model_dump())


cursor: Cursor = connection.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS user_data
    (
        user_id UUID,
        name VARCHAR(255),
        surname VARCHAR(255),
        email VARCHAR(255),
        created_at TIMESTAMPTZ
    )
    """
)


def insert_data():
    """Генерация и вставка данных в таблицу."""
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

        cursor.executemany(
            "INSERT INTO user_data (user_id, name, surname, email, created_at) VALUES (%s, %s, %s, %s, %s)", data
        )

        if (batch + 1) % 100 == 0:
            logger.info(f"Обработано {batch + 1}/{BATCHES} батчей ({(batch + 1) * BATCH_SIZE:,} записей)")

    insertion_time: float = time() - start_time
    insertion_speed: float = round(TOTAL / insertion_time, 2)

    logger.info(f"Скорость вставки: {insertion_speed:,} записей/сек")


def read_data():
    """Чтение данных из таблицы."""
    logger.info("Начало чтения данных...")
    start_time: float = time()

    query = "SELECT user_id, name, surname, email, created_at FROM user_data"
    cursor.execute(query)
    result = cursor.fetchall()

    reading_time: float = time() - start_time
    reading_speed: float = round(TOTAL / reading_time, 2)

    logger.info(f"Скорость чтения: {reading_speed:,} записей/сек")
    logger.info(f"Прочитано записей: {len(result):,}")


if __name__ == "__main__":
    logger.info('Таблица "user_data" создана или уже существует.')
    insert_data()
    read_data()

    cursor.close()
    connection.close()
