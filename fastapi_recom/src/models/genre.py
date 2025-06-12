from typing import List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String

from src.db.postgres import Base


class Genre(Base):
    __tablename__ = "genres"

    genre_movies: Mapped[List["MovieGenre"]] = relationship(back_populates="genre")

    movies: Mapped[List["Movies"]] = relationship(
        "Movies",
        secondary="movie_genre",
        primaryjoin="Genre.id == MovieGenre.genre_id",
        secondaryjoin="Movies.id == MovieGenre.movie_id",
        back_populates="genres"
    )
