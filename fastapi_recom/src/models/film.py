from uuid import UUID
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.postgres import Base
from src.models.genre import Genre


class Movies(Base):
    """Базовая информация о фильме."""

    genre_id: Mapped[UUID] = mapped_column(ForeignKey("genres.id"))

    genres: Mapped[List["Genre"]] = relationship(
        secondary="movie_genre",
        primaryjoin="Movies.id == MovieGenre.movie_id",
        secondaryjoin="Genre.id == MovieGenre.genre_id",
        back_populates="movies"
    )


class MovieGenre(Base):
    movie_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    genre_id: Mapped[UUID] = mapped_column(ForeignKey("genres.id"), primary_key=True)
