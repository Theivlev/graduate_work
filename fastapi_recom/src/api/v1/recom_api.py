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
    return {"message": "This is recomandation system"}
