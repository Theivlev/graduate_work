import logging
from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.crud.base import CRUDBase
from src.models.actions import Actions
from src.models.film import Movies
from src.models.rating import Ratings
from src.models_ml.film import MovieVector
from src.models_ml.user import UserVector
from src.schemas.vectror import MovieVectorCreate, UserVectorCreate

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class VectorService:
    user_vector_crud = CRUDBase(UserVector)
    movie_vector_crud = CRUDBase(MovieVector)

    async def compute_user_vector(self, user_id: UUID, session: AsyncSession) -> dict:
        """
        Вычисляет вектор пользователя на основе его оценок и действий.
        """

        ratings_query = select(Ratings).where(Ratings.user_id == user_id).options(selectinload(Ratings.user))
        result = await session.execute(ratings_query)
        ratings = result.scalars().all()

        actions_count = await session.scalar(select(func.count(Actions.id)).where(Actions.user_id == user_id))

        total_ratings = len(ratings)
        avg_rating = sum(r.rating for r in ratings) / total_ratings if total_ratings else 0.0

        vector = {"avg_rating": avg_rating, "total_ratings": total_ratings, "total_actions": actions_count or 0}

        logger.info(f"Получаем vector {vector}")
        user_vector_dto = UserVectorCreate(user_id=user_id, vector_data=vector)
        logger.info(f"Создаем объект user_vector_dto: {user_vector_dto}")
        await self.user_vector_crud.create(obj_in=user_vector_dto, session=session)
        await session.commit()

        return vector

    async def compute_movie_vector(self, movie_id: UUID, session: AsyncSession) -> dict:
        """
        Вычисляет вектор фильма на основе оценок пользователей.
        """

        movie_query = select(Movies).where(Movies.id == movie_id).options(selectinload(Movies.ratings))
        result = await session.execute(movie_query)
        movie = result.scalars().first()

        if not movie:
            return {}

        ratings = [rating.rating for rating in movie.ratings]

        total_ratings = len(ratings)
        avg_rating = sum(ratings) / total_ratings if total_ratings else 0.0

        vector = {
            "avg_user_rating": avg_rating,
            "total_ratings": total_ratings,
        }

        movie_vector_dto = MovieVectorCreate(movie_id=movie_id, vector_data=vector)
        await self.movie_vector_crud.create(obj_in=movie_vector_dto, session=session)
        await session.commit()

        return vector


vector_service = VectorService()
