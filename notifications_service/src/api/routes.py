from src.api.v1 import notification_router

from fastapi import APIRouter

API_V1: str = "/v1"
main_router = APIRouter()
main_router.include_router(notification_router, prefix=f"{API_V1}/notifications", tags=["notifications"])
