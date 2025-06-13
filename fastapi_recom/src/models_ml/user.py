from uuid import UUID

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres import Base


class UserSimilarity(Base):
    user1_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user2_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    similarity: Mapped[float] = mapped_column()


class UserVector(Base):
    """Вектор предпочтений пользователя"""

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    vector_data: Mapped[dict] = mapped_column(JSON)
