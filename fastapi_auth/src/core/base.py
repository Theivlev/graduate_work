# app/core/base.py

"""Импорты класса Base и всех моделей для Alembic."""
from src.db.postgres import Base  # noqa
from src.models.auth_history import AuthHistory  # noqa
from src.models.role import Role, UserRole  # noqa
from src.models.user import User  # noqa
