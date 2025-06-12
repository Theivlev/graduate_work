from collections import defaultdict
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy import select

from src.models.actions import Actions
from src.models.film import Movies
from src.models.rating import Ratings
from src.models_ml.film import MovieVector
from src.models_ml.user import UserVector
from src.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.vectror import MovieVectorCreate, UserVectorCreate


@dataclass
class VectorService:
    user_vector_crud = CRUDBase(UserVector)
    movie_vector_crud = CRUDBase(MovieVector)

    async def compute_user_vector(self, user_id: UUID, session: AsyncSession) -> dict:
        ratings_query = select(Ratings).where(Ratings.user_id == user_id)
        ratings = (await session.execute(ratings_query)).scalars().all()

        actions_count = await session.scalar(
            select(Actions.id).where(Actions.user_id == user_id)
        )

        total_ratings = len(ratings)
        avg_rating = sum(r.rating for r in ratings) / total_ratings if total_ratings else 0.0

        vector = {
            "avg_rating": avg_rating,
            "total_ratings": total_ratings,
            "total_actions": actions_count or 0
        }

        user_vector_dto = UserVectorCreate(user_id=user_id, vector_data=vector)
        await self.user_vector_crud.create(obj_in=user_vector_dto, session=session)
        await session.commit()

        return vector

    async def compute_movie_vector(self, movie_id: UUID, session: AsyncSession) -> dict:
        movie_query = select(Movies).where(Movies.id == movie_id)
        movie = (await session.execute(movie_query)).scalars().first()

        if not movie:
            return {}

        ratings = [rating.rating for rating in movie.ratings]

        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

        vector = {
            "avg_user_rating": avg_rating,
            "total_ratings": len(ratings),
        }

        movie_vector_dto = MovieVectorCreate(movie_id=movie_id, vector_data=vector)
        await self.movie_vector_crud.create(obj_in=movie_vector_dto, session=session)
        await session.commit()

        return vector


vector_service = VectorService()
