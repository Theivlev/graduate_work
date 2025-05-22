import logging
from typing import AsyncGenerator, List

from aiokafka import ConsumerRecord
from core.base import BaseMessageTranformer
from models.message import MessageDTO


class MessagesTransformer(BaseMessageTranformer):
    """Реализация трансформации сообщений."""

    async def transform(self, messages: List[ConsumerRecord]) -> AsyncGenerator[tuple, None]:
        """
        Асинхронная трансформация сообщений.
        """
        for message in messages:
            try:
                logging.info(f"Обработка сообщения: {message}")

                message_dto = MessageDTO.from_kafka_message(message)

                transformed_message = tuple(message_dto.__dict__.values())
                yield transformed_message

            except Exception as e:
                logging.error(f"Ошибка при обработке сообщения: {e}")
                continue
