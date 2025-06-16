from typing import List

from sqlalchemy.orm import Mapped, relationship
from src.db.postgres import Base


class Users(Base):
    ratings: Mapped[List["Ratings"]] = relationship("Ratings", back_populates="user")  # noqa
