from typing import List

from src.core.user_core import current_user
from src.models.user import User
from src.schemas.auth_shema import AuthGetHistory
from src.services.auth_history_service import AuthHistoryService, get_auth_history

from fastapi import APIRouter, Depends, Request

router = APIRouter()


@router.get(
    "/all", response_model=List[AuthGetHistory], summary="Get all auth_history", description="Get all auth_history"
)
async def get_all_auth_history(
    request: Request,
    auth_service: AuthHistoryService = Depends(get_auth_history),
    limit: int = None,
    user: User = Depends(current_user),
) -> List[AuthGetHistory]:
    try:
        auth_histories = await auth_service.get_history(obj_id=user.id, limit=limit)
        return auth_histories
    except Exception as e:
        raise e
