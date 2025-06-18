import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.postgres import Base


class User(Base):
    """Модель пользователя."""

    name: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20), default="user")
    room_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("room.id"), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    room: Mapped["Room"] = relationship("Room", back_populates="users")  # type: ignore # noqa
    is_superuser: Mapped[bool] = mapped_column(default=False)
    api_key: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    room: Mapped[Optional["Room"]] = relationship("Room", back_populates="users")  # type: ignore # noqa
