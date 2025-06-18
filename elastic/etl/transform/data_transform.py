import logging
from dataclasses import dataclass
from logging import config as logging_config

from models.genre import GenreDTO
from models.movie import MovieDTO
from models.person import PersonInfoDTO
from utils.logger import LOGGING_CONFIG

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


@dataclass
class DataTransform:
    model: type[GenreDTO | MovieDTO | PersonInfoDTO]

    def data_transform(self, batch: list[dict]) -> list[dict]:
        return [self.model(**data).model_dump(by_alias=True) for data in batch]
