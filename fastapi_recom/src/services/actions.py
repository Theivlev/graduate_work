from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.actions import Actions
from src.sсhemas.actions_user import ActionsUserDTO
from src.models.rating import Ratings
from sqlalchemy import select, update, func
from src.models.film import Movies
from src.models.user import Users


@dataclass
class ActionsService:
    actions: CRUDBase = CRUDBase(Actions)
    ratings: CRUDBase = CRUDBase(Ratings)
    movies: CRUDBase = CRUDBase(Movies)
    users: CRUDBase = CRUDBase(Users)

    async def save_action(self, action_dto: ActionsUserDTO, session: AsyncSession):
        user_id = UUID(action_dto.user_id) if isinstance(action_dto.user_id, str) else action_dto.user_id
        movie_id = UUID(action_dto.movies_id) if isinstance(action_dto.movies_id, str) else action_dto.movies_id
        event_time = (
            datetime.fromisoformat(action_dto.event_time)
            if isinstance(action_dto.event_time, str)
            else action_dto.event_time
        )

        existing_user = (await session.execute(
            select(Users).where(Users.id == user_id)
        )).scalars().first()

        if not existing_user:

            user = Users(id=user_id)
            await self.users.create(session, user)

        existing_movie = (await session.execute(
            select(Movies).where(Movies.id == movie_id)
        )).scalars().first()

        if not existing_movie:

            movie = Movies(
                id=movie_id,
                imdb_rating=None
            )
            await self.movies.create(session, movie)

        action = Actions(
            user_id=user_id,
            movie_id=movie_id,
            action=action_dto.actions,
            event_time=event_time,
            event_data=action_dto.event_data,
        )
        await self.actions.create(session, action)

        if action_dto.actions == "rate":
            try:
                rating_value = int(action_dto.event_data)
                if not 1 <= rating_value <= 10:
                    raise ValueError("Рейтинг должен быть от 1 до 10")

                existing_rating = (await session.execute(
                    select(Ratings).where(
                        Ratings.user_id == user_id,
                        Ratings.movie_id == movie_id
                    )
                )).scalars().first()

                if existing_rating:
                    await session.execute(
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
                    await self.ratings.create(session, rating)

            except ValueError as e:
                print(f"Некорректное значение рейтинга: {e}")

        await session.commit()
        return action


actions_service = ActionsService()
