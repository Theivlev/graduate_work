from src.crud.base import BaseMongoCRUD
from src.services.likes import get_likes_service

from fastapi import Depends, HTTPException


async def validate_like_exists(like_id: str, service: BaseMongoCRUD = Depends(get_likes_service)):
    like = await service.get(like_id)
    if not like:
        raise HTTPException(status_code=404, detail="Лайк не найден")
    return like
