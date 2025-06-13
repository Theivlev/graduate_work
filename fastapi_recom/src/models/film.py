from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.postgres import Base


class Movies(Base):
    """Базовая информация о фильме."""

    ratings: Mapped[List["Ratings"]] = relationship("Ratings", back_populates="movie")
