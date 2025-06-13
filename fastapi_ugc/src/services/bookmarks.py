from src.models.bookmark import UserBookmarks
from src.services.base import BaseService


async def get_bookmark_service() -> BaseService:
    """Возвращает экземпляр CRUD-сервиса для работы с коллекцией 'user_bookmarks'."""
    return BaseService(model=UserBookmarks)
