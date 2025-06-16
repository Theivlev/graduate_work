from typing import List
from uuid import UUID

from pydantic import BaseModel


class MovieRecommendationDTO(BaseModel):
    movie_id: UUID


class UserRecommendationResponseDTO(BaseModel):
    user_id: UUID
    recommendations: List[MovieRecommendationDTO]
