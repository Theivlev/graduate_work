from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.postgres import Base


def create_partition(target, connection: Connection, device_types: List[str] = None, **kw) -> None:
    """Создание партиций по типу устройства"""
    device_types = device_types or ["smart", "mobile", "web"]

    try:
        for device_type in device_types:
            partition_table_name = f"auth.auth_history_{device_type}"
            sql = text(
                f"""
                CREATE TABLE IF NOT EXISTS "{partition_table_name}"
                PARTITION OF auth."auth_history"
                FOR VALUES IN ('{device_type}')
                """
            )
            connection.execute(sql)
    except SQLAlchemyError as e:
        raise SQLAlchemyError("Ошибка create_partition для auth_history") from e


class AuthHistory(Base):
    """Таблица истории аутентификации пользователя."""

    __table_args__ = (
        UniqueConstraint("id", "user_device_type"),
        {
            "postgresql_partition_by": "LIST (user_device_type)",
            "listeners": [("after_create", create_partition)],
        },
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("auth.user.id", ondelete="CASCADE"), nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=False)
    user_device_type: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="auth_history")  # noqa
