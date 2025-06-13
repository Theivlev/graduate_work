import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.postgres import Base
from src.models.film import Movies
from src.models.user import Users


class Ratings(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    movie_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id"))
    rating: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    user: Mapped[Users] = relationship("Users", back_populates="ratings")
    movie: Mapped[Movies] = relationship("Movies", back_populates="ratings")
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 10", name="check_rating_range"),)
