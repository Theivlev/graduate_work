from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres import Base


class Actions(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    movie_id: Mapped[UUID] = mapped_column(ForeignKey("movies.id"))
    action: Mapped[dict] = mapped_column(JSON)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    event_data: Mapped[str] = mapped_column(String)
