from src.api.v1 import auth_history_router, role_router, user_router, email_confirm_router

from fastapi import APIRouter

API_V1: str = "/auth/v1"
main_router = APIRouter()
main_router.include_router(user_router, prefix=f"{API_V1}")
main_router.include_router(role_router, prefix=f"{API_V1}/roles", tags=["roles"])
main_router.include_router(auth_history_router, prefix=f"{API_V1}/auth_history", tags=["auth_history"])
main_router.include_router(email_confirm_router, prefix=f"{API_V1}")