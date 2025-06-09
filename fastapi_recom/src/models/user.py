from typing import List
from uuid import UUID


from sqlalchemy.orm import Mapped, relationship
from src.db.postgres import Base
from src.models.rating import Ratings


class User(Base):
    ratings: Mapped[List["Ratings"]] = relationship("Ratings", back_populates="user")
