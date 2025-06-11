from typing import List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String

from src.db.postgres import Base


class Genre(Base):
    """Модель жанра"""
    movies: Mapped[List["Movies"]] = relationship(
        "Movies",
        back_populates="genre"
    )
