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

@dataclass
class VectorService:
    user_vector_crud = CRUDBase(UserVector)
    movie_vector_crud = CRUDBase(MovieVector)

    async def compute_user_vector(self, user_id: UUID, session: AsyncSession) -> dict:

        ratings_query = select(Ratings).where(Ratings.user_id == user_id)
        ratings = (await session.execute(ratings_query)).scalars().all()

        actions_query = select(Actions).where(Actions.user_id == user_id)
        actions = (await session.execute(actions_query)).scalars().all()

        vector = defaultdict(float)
        genre_ratings = defaultdict(list)
        genre_views = defaultdict(int)

        for rating in ratings:
            movie_query = select(Movies).where(Movies.id == rating.movie_id)
            movie = (await self.session.execute(movie_query)).scalars().first()
            if movie:
                for genre in movie.genres:
                    genre_ratings[genre.id].append(rating.rating)

        for action in actions:
            if action.genre_id:
                genre_views[action.genre_id] += 1

        for genre_id in set(genre_ratings.keys()) | set(genre_views.keys()):
            avg_rating = sum(genre_ratings[genre_id]) / len(genre_ratings[genre_id]) if genre_ratings[genre_id] else 0
            vector[f"rating_{genre_id}"] = avg_rating
            vector[f"views_{genre_id}"] = genre_views[genre_id]

        user_vector = UserVector(user_id=user_id, vector_data=dict(vector))
        await self.user_vector_crud.create(self.session, user_vector)
        await self.session.commit()

        return dict(vector)

    async def compute_movie_vector(self, movie_id: UUID) -> dict:
        movie_query = select(Movies).where(Movies.id == movie_id)
        movie = (await self.session.execute(movie_query)).scalars().first()

        vector = {}
        if movie:
            vector["imdb_rating"] = movie.imdb_rating or 0
            for genre in movie.genres:
                vector[f"genre_{genre.id}"] = 1.0

        movie_vector = MovieVector(movie_id=movie_id, vector_data=vector)
        await self.movie_vector_crud.create(self.session, movie_vector)
        await self.session.commit()

        return vector


vector_service = VectorService()