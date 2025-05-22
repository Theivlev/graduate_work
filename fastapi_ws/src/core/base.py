"""Импорты класса Base и всех моделей для Alembic."""
from src.db.postgres import Base  # noqa
from src.models.message_model import Message  # noqa
from src.models.room_model import Room  # noqa
from src.models.user_model import User  # noqa
