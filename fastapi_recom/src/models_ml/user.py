from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres import Base


class UserSimilarity(Base):
    user1_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user2_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    similarity: Mapped[float] = mapped_column()
