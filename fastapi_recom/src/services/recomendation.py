from dataclasses import dataclass
from typing import List
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db.postgres import get_async_session
from src.models.rating import Ratings
from src.models.film import Movies
from src.models_ml.film import MovieSimilarity
from src.models_ml.user import UserSimilarity


def get_recommendation(session: AsyncSession = Depends(get_async_session)) -> "RecomendationService":
    """Функция для получения истории входов."""
    return RecomendationService(session)


from dataclasses import dataclass
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.rating import Ratings
from src.models.film import Movies
from src.models_ml.film import MovieSimilarity
from src.models_ml.user import UserSimilarity
from src.schemas.recomendation import (
    MovieRecommendationDTO,
    UserRecommendationResponseDTO,
    GeneralRecommendationResponseDTO
)


@dataclass
class RecomendationService:
    session: AsyncSession

    async def get_recommendations(self, user_id: UUID, limit: int = 10) -> UserRecommendationResponseDTO:
        similarities = (await self.session.execute(
            select(UserSimilarity).where(UserSimilarity.user1_id == user_id)
        )).scalars().all()

        similar_users = sorted(similarities, key=lambda x: x.similarity, reverse=True)[:5]

        recommended_movie_ids = set()

        for sim in similar_users:
            ratings = (await self.session.execute(
                select(Ratings).where(Ratings.user_id == sim.user2_id, Ratings.rating >= 7)
            )).scalars().all()

            for rating in ratings:
                recommended_movie_ids.add(rating.movie_id)

        recommendations = [MovieRecommendationDTO(movie_id=mid) for mid in recommended_movie_ids]

        return UserRecommendationResponseDTO(
            user_id=user_id,
            recommendations=recommendations[:limit]
        )

    async def get_general_recommendations(self, limit: int = 10) -> GeneralRecommendationResponseDTO:
        popular_movies = (await self.session.execute(
            select(Movies).where(Movies.imdb_rating >= 7.0).order_by(Movies.ratings.desc()).limit(10)
        )).scalars().all()

        recommended_movie_ids = set()

        for movie in popular_movies:
            similarities = (await self.session.execute(
                select(MovieSimilarity).where(MovieSimilarity.movie1_id == movie.id)
            )).scalars().all()

            similar_movies = sorted(similarities, key=lambda x: x.similarity, reverse=True)[:5]

            for sim in similar_movies:
                recommended_movie_ids.add(sim.movie2_id)

        recommendations = [MovieRecommendationDTO(movie_id=mid) for mid in recommended_movie_ids]

        return GeneralRecommendationResponseDTO(recommendations=recommendations[:limit])