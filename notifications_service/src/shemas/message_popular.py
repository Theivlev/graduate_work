import uuid
from typing import Dict, List, Literal
from uuid import UUID

from src.models.dto import AbstractDTO


import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MessagePopularMoviesDTO(AbstractDTO):
    id: UUID
    user_id: str
    body: str
    recipient: str
    channel: Literal["email", "push"]
    movies: List[Dict[str, str]]
    notification_queue: str = "popular_movies"

    @staticmethod
    def create(user_data: dict, channel: str = "email") -> "MessagePopularMoviesDTO":
        """
        Создает объект MessagePopularMoviesDTO на основе данных.
        """
        try:
            logger.info('МЫ ЗАХОДИТ В ОТПРАВКУ MESSAGES')
            if not all(key in user_data for key in ["user_id", "email", "movies"]):
                raise ValueError("В user_data отсутствуют обязательные поля: user_id, email, movies")
            body = "У вас новые рекомендации фильмов!"

            return MessagePopularMoviesDTO(
                id=uuid.uuid4(),
                user_id=user_data.get("user_id"),
                body=body,
                recipient=user_data.get("email"),
                channel=channel,
                movies=user_data.get("movies", []),
                notification_type="popular_movies",
            )
        except Exception as e:
            raise ValueError(f"Ошибка при создании MessagePopularMoviesDTO: {str(e)}")
