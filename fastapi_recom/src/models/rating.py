
import datetime
from sqlalchemy import ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.db.postgres import Base
from src.models.film import Movies
from src.models.user import User


class Ratings(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    rating: Mapped[int] = mapped_column(Integer, check_constraint="rating >= 1 AND rating <= 10")
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )
    user: Mapped[User] = relationship("Users", back_populates="ratings")
    movie: Mapped[Movies] = relationship("Movies", back_populates="ratings")
