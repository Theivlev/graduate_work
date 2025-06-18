from beanie import init_beanie
from src.models.bookmark import UserBookmarks
from src.models.like import UserLikes
from src.models.review import UserReviews


async def init_db(db):
    """
    Инициализация Beanie с MongoDB.
    """
    await init_beanie(database=db, document_models=[UserBookmarks])
    await init_beanie(database=db, document_models=[UserLikes])
    await init_beanie(database=db, document_models=[UserReviews])
