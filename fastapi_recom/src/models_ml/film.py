from uuid import UUID

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres import Base


class MovieSimilarity(Base):
    """Предвычисленные значения сходства между фильмами."""

    movie1_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    movie2_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    similarity: Mapped[float] = mapped_column()


class MovieVector(Base):
    """Вектор характеристик фильма"""

    movie_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    vector_data: Mapped[dict] = mapped_column(JSON)
