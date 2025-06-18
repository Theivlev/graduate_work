from beanie import init_beanie
from src.models.movies import MovieViewStats
from src.models.notifications import NotificationRecord
from src.models.user import User


async def init_db(db):
    """
    Инициализация Beanie с MongoDB.
    """
    await init_beanie(database=db, document_models=[MovieViewStats, NotificationRecord, User])
