from dataclasses import dataclass
from typing import List
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db.postgres import get_async_session
from src.models_ml.user import UserSimilarity
from src.models_ml.film import MovieSimilarity


def get_recommendation(session: AsyncSession = Depends(get_async_session)) -> "RecomendationService":
    """Функция для получения истории входов."""
    return RecomendationService(session)


@dataclass
class RecomendationService:
    session: AsyncSession
    auth: CRUDBase = CRUDBase(UserSimilarity)
    rating: CRUDBase = CRUDBase(MovieSimilarity)

    async def get_recommendations():
        pass
