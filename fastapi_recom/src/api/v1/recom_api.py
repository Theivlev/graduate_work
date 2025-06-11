from fastapi_cache.decorator import cache

from fastapi import APIRouter, Depends
from src.services.recomendation import get_recommendation, RecomendationService

router = APIRouter()


@router.get(
    "/",
    summary="Get recom",
    description="Get recomendations for users.",
)
@cache(expire=30)
async def get_recom(
    reccomandation_service: RecomendationService = Depends(get_recommendation),
):
    try:
        reccomandation = await reccomandation_service.get_recommendations(user_id=...)
        pass
    except Exception as e:
        raise e
