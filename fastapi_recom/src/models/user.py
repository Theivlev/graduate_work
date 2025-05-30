from typing import List
from uuid import UUID


from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.postgres import Base
from src.models.rating import Ratings


class User(Base):
    name: Mapped[str] = mapped_column(nullable=True)
    surname: Mapped[str] = mapped_column(nullable=True)
    patronymic: Mapped[str] = mapped_column(nullable=True)
    ratings: Mapped[List["Ratings"]] = relationship("Ratings", back_populates="user")