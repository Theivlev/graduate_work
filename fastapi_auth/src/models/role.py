from enum import Enum
from typing import List
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres import Base


class Permissions(Enum):
    """Перечисление возможных прав доступа к ресурсу."""

    read = "read"
    write = "write"
    delete = "delete"
    update = "update"


class Role(Base):
    """Модель роли пользователя."""

    name: Mapped[str]
    permissions: Mapped[List[Permissions]] = mapped_column(sa.ARRAY(sa.Enum(Permissions)), nullable=False)


class UserRole(Base):
    """Модель связи пользователя и роли."""

    user_id: Mapped[UUID] = mapped_column(sa.ForeignKey("auth.user.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[UUID] = mapped_column(sa.ForeignKey("auth.role.id", ondelete="CASCADE"), primary_key=True)
