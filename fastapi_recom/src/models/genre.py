from typing import List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String

from src.db.postgres import Base
from src.models.film import Movies


class Genre(Base):
    """Модель жанра"""

    name: Mapped[str] = mapped_column(String(90))
    movies: Mapped[List["Movies"]] = relationship(
        "Movies",
        back_populates="genre"
    )
