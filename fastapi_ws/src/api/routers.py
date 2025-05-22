from src.api.v1 import ws_router

from fastapi import APIRouter

API_V1: str = "/ws/v1"
main_router = APIRouter()
main_router.include_router(ws_router, prefix=f"{API_V1}/chat", tags=["Chat"])
