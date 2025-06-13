from src.crud.base import ModelType
from src.models.review import UserReviews
from src.services.base import BaseService


class ReviewsService(BaseService):
    """Класс-сервис для работы с коллекцией 'user_reviews'."""

    async def create(self, data: dict) -> ModelType:
        """Создает нового объекта в базе данных."""
        result = await self.crud.create(data)
        await self.send_kafka("create", data.get("user_id"), data.get("movie_id"), data.get("review_text"))
        return result

    async def update(self, id_: str, data: dict) -> ModelType | None:
        """Обновляет объект в базе данных."""
        result = await self.crud.update(id_, data)
        await self.send_kafka("update", data.get("user_id"), data.get("movie_id"), data.get("review_text"))
        return result


async def get_reviews_service() -> BaseService:
    """Возвращает экземпляр CRUD-сервиса для работы с коллекцией 'user_reviews'."""
    return ReviewsService(model=UserReviews)
