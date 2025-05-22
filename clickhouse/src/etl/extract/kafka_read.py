import logging
from dataclasses import dataclass
from typing import AsyncGenerator, List

from aiokafka import AIOKafkaConsumer
from core.base import BaseMessageReader
from core.config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@dataclass
class KafkaReader(BaseMessageReader):
    consumer: AIOKafkaConsumer = None

    async def __aenter__(self):
        logging.info("Инициализация KafkaConsumer...")
        self.consumer = AIOKafkaConsumer(
            settings.topic,
            bootstrap_servers=settings.kafka_brokers,
            group_id=settings.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await self.consumer.start()
        logging.info(f"KafkaConsumer успешно запущен для топика '{settings.topic}' с группой '{settings.group_id}'.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.consumer:
            logging.info("Остановка KafkaConsumer...")
            await self.consumer.stop()
            logging.info("KafkaConsumer успешно остановлен.")

    async def read(self, batch_size: int = 10) -> AsyncGenerator[List[bytes], None]:
        messages = []
        logging.info("Начало чтения сообщений...")
        try:
            logging.info("Начинаю цикл...")
            async for message in self.consumer:
                logging.info(f"Получено сообщение: {message}")
                messages.append(message)

                if len(messages) >= batch_size:
                    logging.info(f"Достигнут размер batch: {batch_size}. Передача сообщений в обработку.")
                    yield messages
                    messages.clear()
        finally:
            if messages:
                logging.info("Передача оставшихся сообщений в обработку.")
                yield messages

    async def commit(self):
        if self.consumer:
            logging.info("Коммит сообщений...")
            await self.consumer.commit()
            logging.info("Сообщения успешно закоммичены.")
