from dataclasses import dataclass
from typing import List
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_async_session
from src.models.rating import Ratings
from src.models.film import Movies
from src.models_ml.film import MovieSimilarity
from src.models_ml.user import UserSimilarity

from src.schemas.recomendation import (
    MovieRecommendationDTO,
    UserRecommendationResponseDTO,
    GeneralRecommendationResponseDTO
)


def get_recommendation(session: AsyncSession = Depends(get_async_session)) -> "RecomendationService":
    """Функция для получения истории входов."""
    return RecomendationService(session)


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
        subquery = (
            select(Ratings.movie_id)
            .group_by(Ratings.movie_id)
            .having(func.avg(Ratings.rating) >= 7.0)
            .subquery()
        )

        stmt = (
            select(Movies)
            .join(subquery, Movies.id == subquery.c.movie_id)
            .limit(10)
        )

        result = await self.session.execute(stmt)
        popular_movies = result.scalars().all()

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
