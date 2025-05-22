from src.crud.base import BaseMongoCRUD
from src.models.bookmark import UserBookmarks


async def get_bookmark_service() -> BaseMongoCRUD:
    """
    Возвращает экземпляр CRUD-сервиса для работы с коллекцией 'user_bookmarks'.
    """
    return BaseMongoCRUD(model=UserBookmarks)
