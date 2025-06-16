from typing import List

from sqlalchemy.orm import Mapped, relationship
from src.db.postgres import Base


class Movies(Base):
    """Базовая информация о фильме."""

    ratings: Mapped[List["Ratings"]] = relationship("Ratings", back_populates="movie")  # noqa
