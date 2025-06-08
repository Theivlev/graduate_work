from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Dict

from pydantic import BaseModel, Field


class ActionsUserDTO(BaseModel):
    user_id: UUID | str
    movies_id: UUID | str
    genre_id: UUID | str | None = None
    actions: str | dict
    event_time: datetime | str
    event_data: str
