from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db.postgres import get_async_session
from src.models.actions import Actions
from src.sсhemas.actions_user import ActionsUserDTO
from src.models.rating import Ratings
from sqlalchemy import select, update, func
from src.models.film import Movies
from src.models.user import User


def get_actions(session: AsyncSession = Depends(get_async_session)) -> "ActionsService":
    """Функция для получения истории входов."""
    return ActionsService(session)


@dataclass
class ActionsService:
    session: AsyncSession
    actions: CRUDBase = CRUDBase(Actions)
    ratings: CRUDBase = CRUDBase(Ratings)
    movies: CRUDBase = CRUDBase(Movies)
    users: CRUDBase = CRUDBase(User)

    async def save_action(self, action_dto: ActionsUserDTO):
        user_id = UUID(action_dto.user_id) if isinstance(action_dto.user_id, str) else action_dto.user_id
        movie_id = UUID(action_dto.movies_id) if isinstance(action_dto.movies_id, str) else action_dto.movies_id
        genre_id = UUID(action_dto.genre_id) if isinstance(action_dto.genre_id, str) else action_dto.genre_id
        event_time = (
            datetime.fromisoformat(action_dto.event_time)
            if isinstance(action_dto.event_time, str)
            else action_dto.event_time
        )

        existing_user = (await self.session.execute(
            select(User).where(User.id == user_id)
        )).scalars().first()

        if not existing_user:

            user = User(id=user_id)
            await self.users.create(self.session, user)

        existing_movie = (await self.session.execute(
            select(Movies).where(Movies.id == movie_id)
        )).scalars().first()

        if not existing_movie:

            movie = Movies(
                id=movie_id,
                imdb_rating=None
            )
            await self.movies.create(self.session, movie)

        action = Actions(
            user_id=user_id,
            movie_id=movie_id,
            genre_id=genre_id,
            action=action_dto.actions,
            event_time=event_time,
            event_data=action_dto.event_data,
        )
        await self.actions.create(self.session, action)

        if action_dto.actions == "rate":
            try:
                rating_value = int(action_dto.event_data)
                if not 1 <= rating_value <= 10:
                    raise ValueError("Рейтинг должен быть от 1 до 10")

                existing_rating = (await self.session.execute(
                    select(Ratings).where(
                        Ratings.user_id == user_id,
                        Ratings.movie_id == movie_id
                    )
                )).scalars().first()

                if existing_rating:
                    await self.session.execute(
                        update(Ratings)
                        .where(Ratings.user_id == user_id, Ratings.movie_id == movie_id)
                        .values(rating=rating_value, timestamp=func.now())
                    )
                else:
                    rating = Ratings(
                        user_id=user_id,
                        movie_id=movie_id,
                        rating=rating_value,
                        timestamp=event_time
                    )
                    await self.ratings.create(self.session, rating)

            except ValueError as e:
                print(f"Некорректное значение рейтинга: {e}")

        await self.session.commit()
        return action
