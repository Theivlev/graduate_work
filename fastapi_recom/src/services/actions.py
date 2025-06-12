from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.actions import Actions
from src.schemas.actions_user import ActionsUserDTO
from src.models.rating import Ratings
from sqlalchemy import select, update, func
from src.models.film import Movies
from src.models.user import Users
from src.schemas.movies import MovieSchema
from src.schemas.rating import RatingSchema
from src.schemas.user import UserSchema


import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ActionsService:
    actions: CRUDBase = CRUDBase(Actions)
    ratings: CRUDBase = CRUDBase(Ratings)
    movies: CRUDBase = CRUDBase(Movies)
    users: CRUDBase = CRUDBase(Users)

    async def save_action(self, action_dto: ActionsUserDTO, session: AsyncSession):
        logger.info(f"Начало обработки события {action_dto}")

        try:
            user_id = UUID(action_dto.user_id) if isinstance(action_dto.user_id, str) else action_dto.user_id
            movie_id = UUID(action_dto.movie_id) if isinstance(action_dto.movie_id, str) else action_dto.movie_id
            event_time = (
                datetime.fromisoformat(action_dto.event_time)
                if isinstance(action_dto.event_time, str)
                else action_dto.event_time
            )

            existing_user = await self.users.get(obj_id=user_id, session=session)
            if not existing_user:
                user_create = UserSchema(id=user_id)
                await self.users.create(obj_in=user_create, session=session)

            existing_movie = await self.movies.get(obj_id=movie_id, session=session)
            if not existing_movie:
                movie_create = MovieSchema(id=movie_id)
                await self.movies.create(obj_in=movie_create, session=session)

            await self.actions.create(obj_in=action_dto, session=session)

            if action_dto.action.get('type') == "rate":
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
                        rating_create = RatingSchema(
                            user_id=user_id,
                            movie_id=movie_id,
                            rating=rating_value,
                            timestamp=event_time
                        )
                        await self.ratings.create(obj_in=rating_create, session=session)

                except ValueError as e:
                    logger.warning(f"Ошибка при обработке рейтинга: {e}")
                    print(f"Некорректное значение рейтинга: {e}")

            await session.commit()
            return True

        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
            await session.rollback()
            raise


actions_service = ActionsService()
