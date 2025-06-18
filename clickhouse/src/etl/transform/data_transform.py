import json
import logging
from typing import AsyncGenerator, List

from aiokafka import ConsumerRecord
from pydantic import ValidationError

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

                try:
                    decode_value: dict = json.loads(message.value.decode("utf-8"))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Ошибка декодирования значения сообщения: {e}")

                try:
                    message_dto = MessageDTO.model_validate(decode_value)
                except ValidationError as e:
                    raise ValueError(f"Ошибка валидации сообщения: {e}")

                logging.info(f"Полученное сообщение: {message_dto.model_dump()}")
                logging.info(f"Трансформированное сообщение: {tuple(message_dto.model_dump().values())}")
                transformed_message = tuple(message_dto.model_dump().values())
                yield transformed_message

            except Exception as e:
                logging.error(f"Ошибка при обработке сообщения: {e}")
                continue
