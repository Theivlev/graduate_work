from datetime import datetime
from uuid import UUID

from .dto import AbstractDTO


class ActionsUserDTO(AbstractDTO):
    user_id: UUID
    movie_id: UUID
    action: str | dict
    event_time: datetime
    event_data: str | dict
