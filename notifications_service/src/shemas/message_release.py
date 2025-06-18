import uuid
from typing import Literal
from uuid import UUID

from src.models.dto import AbstractDTO


class MessageEpisodeReleaseDTO(AbstractDTO):
    id: UUID
    user_id: str
    body: str
    recipient: str
    channel: Literal["email", "push"]
    series_id: str
    episode: str
    notification_queue: str = "episode_release"

    @staticmethod
    def create(user_data: dict, channel: str = "email") -> "MessageEpisodeReleaseDTO":
        """
        Создает объект MessageEpisodeReleaseDTO на основе данных.
        """
        try:
            if not all(key in user_data for key in ["user_id", "email", "series_id", "episode"]):
                raise ValueError("В user_data отсутствуют обязательные поля: user_id, email, series_id, episode")

            body = f"Новый эпизод сериала (ID: {user_data['series_id']}) доступен: {user_data['episode']}!"

            return MessageEpisodeReleaseDTO(
                id=uuid.uuid4(),
                user_id=user_data.get("user_id"),
                body=body,
                recipient=user_data.get("email"),
                channel=channel,
                series_id=user_data.get("series_id"),
                episode=user_data["episode"],
                notification_type="episode_release",
            )
        except Exception as e:
            raise ValueError(f"Ошибка при создании MessageEpisodeReleaseDTO: {str(e)}")
