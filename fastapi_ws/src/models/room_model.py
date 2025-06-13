import time
from typing import Any, Dict, List

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from src.db.postgres import Base


class Room(Base):
    """Модель комнаты."""

    name: Mapped[str] = mapped_column(nullable=False)
    message_history: Mapped[list] = mapped_column(JSONB, default=list)
    users: Mapped[List["User"]] = relationship("User", back_populates="room")

    def add_message(self, message: Dict[str, Any]):
        if self.message_history is None:
            self.message_history = []
        encoded_message = {
            "text": message.get("text", ""),
            "username": message.get("username", "System"),
            "timestamp": message.get("timestamp", int(time.time())),
            "role": message.get("role", "user"),
            "type": message.get("type", "message"),
        }
        new_history = list(self.message_history)
        new_history.append(encoded_message)
        self.message_history = new_history
        flag_modified(self, "message_history")
