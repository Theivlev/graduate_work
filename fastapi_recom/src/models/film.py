from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from src.db.postgres import Base
from src.models.genre import Genre
from typing import List


class Movies(Base):
    """Базовая информация о фильме."""

    title: Mapped[str] = mapped_column(String(255))
    imdb_rating: Mapped[float | None] = mapped_column(nullable=True)

    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))

    genres: Mapped[List["Genre"]] = relationship(
        secondary="movie_genre",
        back_populates="movies"
    )


class MovieGenre(Base):
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), primary_key=True)
