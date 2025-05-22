from src.api.v1 import recom_router

from fastapi import APIRouter

API_V1: str = "/recom/v1"
main_router = APIRouter()
main_router.include_router(recom_router, prefix=f"{API_V1}/recom", tags=["recomendations"])
