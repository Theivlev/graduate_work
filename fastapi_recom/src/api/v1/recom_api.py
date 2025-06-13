from fastapi_cache.decorator import cache

from fastapi import APIRouter, Depends, UUID4
from src.services.recomendation import get_recommendation, RecomendationService
from src.schemas.recomendation import GeneralRecommendationResponseDTO, UserRecommendationResponseDTO
router = APIRouter()


@router.get(
    "/user/{user_id}",
    summary="Получить рекомендации для пользователя",
    description="Получить персонализированные рекомендации на основе предпочтений пользователя.",
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
    summary="Получить общие рекомендации",
    description="Получить топовые рекомендации на основе популярных и похожих фильмов.",
    response_model=GeneralRecommendationResponseDTO
)
@cache(expire=60)
async def get_general_recom(
    recommendation_service: RecomendationService = Depends(get_recommendation),
):
    return await recommendation_service.get_general_recommendations()
