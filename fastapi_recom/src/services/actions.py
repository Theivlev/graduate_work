from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db.postgres import get_async_session
from src.models.actions import Actions
from src.shemas.actions_user import ActionsUserDTO


def get_actions(session: AsyncSession = Depends(get_async_session)) -> "ActionsService":
    """Функция для получения истории входов."""
    return ActionsService(session)


@dataclass
class ActionsService:
    session: AsyncSession
    actions: CRUDBase = CRUDBase(Actions)

    async def save_action(self, action_dto: ActionsUserDTO):

        user_id = UUID(action_dto.user_id) if isinstance(action_dto.user_id, str) else action_dto.user_id
        movie_id = UUID(action_dto.movies_id) if isinstance(action_dto.movies_id, str) else action_dto.movies_id
        genre_id = UUID(action_dto.genre_id) if isinstance(action_dto.genre_id, str) else action_dto.genre_id
        event_time = (
            datetime.fromisoformat(action_dto.event_time)
            if isinstance(action_dto.event_time, str)
            else action_dto.event_time
        )

        action = Actions(
            user_id=user_id,
            movie_id=movie_id,
            genre_id=genre_id,
            action=action_dto.actions,
            event_time=event_time,
            event_data=action_dto.event_data,
        )

        await self.actions.create(self.session, action)
        await self.session.commit()
        return action
