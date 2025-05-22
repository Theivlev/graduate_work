from src.crud.base import BaseMongoCRUD
from src.models.like import UserLikes


async def get_likes_service() -> BaseMongoCRUD:
    """
    Возвращает экземпляр CRUD-сервиса для работы с коллекцией 'user_likes'.
    """
    return BaseMongoCRUD(model=UserLikes)
