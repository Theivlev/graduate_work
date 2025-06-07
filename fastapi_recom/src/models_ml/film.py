from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from src.db.postgres import Base


class MovieSimilarity(Base):
    """Предвычисленные значения сходства между фильмами."""

    movie1_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    movie2_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    similarity: Mapped[float] = mapped_column()
