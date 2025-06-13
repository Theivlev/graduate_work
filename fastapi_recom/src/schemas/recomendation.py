from uuid import UUID
from typing import List
from pydantic import BaseModel


class MovieRecommendationDTO(BaseModel):
    movie_id: UUID


class UserRecommendationResponseDTO(BaseModel):
    user_id: UUID
    recommendations: List[MovieRecommendationDTO]


class GeneralRecommendationResponseDTO(BaseModel):
    recommendations: List[MovieRecommendationDTO]
