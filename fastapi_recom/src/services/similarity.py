from dataclasses import dataclass
from uuid import UUID

import numpy as np
from sqlalchemy import select
from sklearn.metrics.pairwise import cosine_similarity

from src.crud.base import CRUDBase
from src.models_ml.film import MovieSimilarity, MovieVector
from src.models_ml.user import UserSimilarity, UserVector
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class SimilarityService:
    user_similarity_crud = CRUDBase(UserSimilarity)
    movie_similarity_crud = CRUDBase(MovieSimilarity)

    async def compute_user_similarity(self, user1_id: UUID, user2_id: UUID, session: AsyncSession) -> float:

        user1_vector: UserVector = (await session.execute(
            select(UserVector).where(UserVector.user_id == user1_id)
        )).scalars().first()
        user2_vector: UserVector = (await session.execute(
            select(UserVector).where(UserVector.user_id == user2_id)
        )).scalars().first()

        if not user1_vector or not user2_vector:
            return 0.0

        keys = set(user1_vector.vector_data.keys()) | set(user2_vector.vector_data.keys())
        vec1 = np.array([user1_vector.vector_data.get(k, 0) for k in keys])
        vec2 = np.array([user2_vector.vector_data.get(k, 0) for k in keys])

        similarity = cosine_similarity([vec1], [vec2])[0][0]

        user_similarity = UserSimilarity(user1_id=user1_id, user2_id=user2_id, similarity=similarity)
        await self.user_similarity_crud.create(session, user_similarity)
        await session.commit()

        return similarity

    async def compute_movie_similarity(self, movie1_id: UUID, movie2_id: UUID, session: AsyncSession) -> float:
        movie1_vector = (await session.execute(
            select(MovieVector).where(MovieVector.movie_id == movie1_id)
        )).scalars().first()
        movie2_vector = (await session.execute(
            select(MovieVector).where(MovieVector.movie_id == movie2_id)
        )).scalars().first()

        if not movie1_vector or not movie2_vector:
            return 0.0

        keys = set(movie1_vector.vector_data.keys()) | set(movie2_vector.vector_data.keys())
        vec1 = np.array([movie1_vector.vector_data.get(k, 0) for k in keys])
        vec2 = np.array([movie2_vector.vector_data.get(k, 0) for k in keys])

        similarity = cosine_similarity([vec1], [vec2])[0][0]

        movie_similarity = MovieSimilarity(movie1_id=movie1_id, movie2_id=movie2_id, similarity=similarity)
        await self.movie_similarity_crud.create(obj_in=movie_similarity, session=session)
        await session.commit()

        return similarity


similarity_service = SimilarityService()
