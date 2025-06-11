from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ActionsUserDTO(BaseModel):
    user_id: UUID | str
    movies_id: UUID | str
    genre_id: UUID | str | None = None
    actions: str | dict
    event_time: datetime | str
    event_data: str | dict
