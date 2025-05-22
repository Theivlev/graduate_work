from src.crud.base import BaseMongoCRUD
from src.models.review import UserReviews


async def get_reviews_service() -> BaseMongoCRUD:
    """
    Возвращает экземпляр CRUD-сервиса для работы с коллекцией 'user_reviews'.
    """
    return BaseMongoCRUD(model=UserReviews)
