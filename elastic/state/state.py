import logging
from dataclasses import dataclass
from logging import config as logging_config

from utils.logger import LOGGING_CONFIG

from .base_storage import BaseStorage

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


@dataclass
class State:
    """Класс для работы с состояниями."""

    storage: BaseStorage

    def set_state(self, key: str, value: str) -> None:
        """Устанавливает состояние по ключу."""
        logging.info("Сохраняем состояние %s", key)
        self.storage.save_state(key, value)

    def get_state(self, key: str) -> str | None:
        """Получает состояние по ключу."""
        logging.info("Получаем текущее состояние %s", key)
        return self.storage.retrieve_state(key)
