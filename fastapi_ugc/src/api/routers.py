from src.api.v1 import bookmarks_router, likes_router, reviews_router

from fastapi import APIRouter

API_V1: str = "/social/v1"
main_router = APIRouter()
main_router.include_router(bookmarks_router, prefix=f"{API_V1}/bookmarks", tags=["bookmarks"])
main_router.include_router(likes_router, prefix=f"{API_V1}/likes", tags=["likes"])
main_router.include_router(reviews_router, prefix=f"{API_V1}/reviews", tags=["reviews"])
