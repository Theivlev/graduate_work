from typing import List
from uuid import UUID

from pydantic import BaseModel


class MovieRecommendationDTO(BaseModel):
    movie_id: UUID


class GeneralRecommendationResponseDTO(BaseModel):
    recommendations: List[MovieRecommendationDTO]
