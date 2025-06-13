from fastapi_cache.decorator import cache

from fastapi import APIRouter, Depends, UUID4
from src.services.recomendation import get_recommendation, RecomendationService
from src.schemas.recomendation import GeneralRecommendationResponseDTO, UserRecommendationResponseDTO
router = APIRouter()


@router.get(
    "/user/{user_id}",
    summary="Get user recommendations",
    description="Get personalized recommendations based on user preferences.",
    response_model=UserRecommendationResponseDTO
)
@cache(expire=30)
async def get_user_recom(
    user_id: UUID4,
    recommendation_service: RecomendationService = Depends(get_recommendation),
):
    return await recommendation_service.get_recommendations(user_id=user_id)


@router.get(
    "/general",
    summary="Get general recommendations",
    description="Get top recommendations based on popular and similar movies.",
    response_model=GeneralRecommendationResponseDTO
)
@cache(expire=60)
async def get_general_recom(
    recommendation_service: RecomendationService = Depends(get_recommendation),
):
    return await recommendation_service.get_general_recommendations()