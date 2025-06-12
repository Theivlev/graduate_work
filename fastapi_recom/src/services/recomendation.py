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


@dataclass
class RecomendationService:
    session: AsyncSession
    auth: CRUDBase = CRUDBase(UserSimilarity)
    rating: CRUDBase = CRUDBase(MovieSimilarity)

    async def get_recommendations(self, user_id: UUID, limit: int = 10) -> list[dict]:

        similarities = (await self.session.execute(
            select(UserSimilarity).where(UserSimilarity.user1_id == user_id)
        )).scalars().all()

        similar_users = sorted(similarities, key=lambda x: x.similarity, reverse=True)[:5]

        recommended_movies = []
        for sim in similar_users:
            ratings = (await self.session.execute(
                select(Ratings).where(Ratings.user_id == sim.user2_id, Ratings.rating >= 7)
            )).scalars().all()
            for rating in ratings:
                movie = (await self.session.execute(
                    select(Movies).where(Movies.id == rating.movie_id)
                )).scalars().first()
                if movie:
                    recommended_movies.append({
                        "movie_id": movie.id,
                        "ratings": movie.ratings,
                        "similarity": sim.similarity
                    })

        recommended_movies = sorted(
            recommended_movies,
            key=lambda x: (x["similarity"], x["ratings"] or 0),
            reverse=True
        )[:limit]

        return recommended_movies

    async def get_general_recommendations(self, limit: int = 10) -> List[dict]:
        """Получить общие рекомендации на основе сходства фильмов."""

        popular_movies = (await self.session.execute(
            select(Movies).where(Movies.imdb_rating >= 7.0).order_by(Movies.ratings.desc()).limit(10)
        )).scalars().all()

        recommended_movies = []

        for movie in popular_movies:
            similarities = (await self.session.execute(
                select(MovieSimilarity).where(MovieSimilarity.movie1_id == movie.id)
            )).scalars().all()

            similar_movies = sorted(similarities, key=lambda x: x.similarity, reverse=True)[:5]

            for sim in similar_movies:
                similar_movie = (await self.session.execute(
                    select(Movies).where(Movies.id == sim.movie2_id)
                )).scalars().first()
                if similar_movie:
                    recommended_movies.append({
                        "movie_id": similar_movie.id,
                        "ratings": similar_movie.ratings,
                        "similarity": sim.similarity
                    })

        recommended_movies = sorted(
            recommended_movies,
            key=lambda x: (x["similarity"], x["ratings"] or 0),
            reverse=True
        )[:limit]

        return recommended_movies
