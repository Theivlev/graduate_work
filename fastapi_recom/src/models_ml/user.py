from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from src.db.postgres import Base
from uuid import UUID


class UserSimilarity(Base):
    user1_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user2_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    similarity: Mapped[float] = mapped_column()


class UserVector(Base):
    """Вектор предпочтений пользователя"""
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    vector_data: Mapped[dict] = mapped_column(JSON)
