from fastapi_cache.decorator import cache
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/",
    summary="Get recom",
    description="Get recomendations for users.",
)
@cache(expire=60)
async def get_recom():
    return {'message': 'This is recomandation system'}
