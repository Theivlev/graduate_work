from uuid import UUID

from fastapi_cache.decorator import cache
from src.rabbitmq.enums import RoutingKeys
from src.rabbitmq.exchanges import EXCHANGES
from src.rabbitmq.producer import publish
from src.rabbitmq.queues import QUEUES
from src.schemas.recomendation import GeneralRecommendationResponseDTO, UserRecommendationResponseDTO
from src.services.recomendation import RecomendationService, get_recommendation

from fastapi import APIRouter, Depends

router = APIRouter()


@router.get(
    "/user/{user_id}",
    summary="Получить рекомендации для пользователя",
    description="Получить персонализированные рекомендации на основе предпочтений пользователя.",
    response_model=UserRecommendationResponseDTO,
)
@cache(expire=30)
async def get_user_recom(
    user_id: UUID,
    recommendation_service: RecomendationService = Depends(get_recommendation),
):
    recommendation = await recommendation_service.get_recommendations(user_id=user_id)
    await publish(
        message=recommendation,
        queue=QUEUES[RoutingKeys.RECOMMENDATIONS],
        exchange=EXCHANGES[RoutingKeys.RECOMMENDATIONS],
    )
    return recommendation


@router.get(
    "/general",
    summary="Получить общие рекомендации",
    description="Получить топовые рекомендации на основе популярных и похожих фильмов.",
    response_model=GeneralRecommendationResponseDTO,
)
@cache(expire=60)
async def get_general_recom(
    recommendation_service: RecomendationService = Depends(get_recommendation),
):
    recommendation = await recommendation_service.get_general_recommendations()
    await publish(
        message=recommendation,
        queue=QUEUES[RoutingKeys.RECOMMENDATIONS],
        exchange=EXCHANGES[RoutingKeys.RECOMMENDATIONS],
    )
    return recommendation
