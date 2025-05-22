from src.crud.base import BaseMongoCRUD
from src.services.bookmarks import get_bookmark_service

from fastapi import Depends, HTTPException


async def validate_bookmark_exists(bookmark_id: str, service: BaseMongoCRUD = Depends(get_bookmark_service)):
    bookmark = await service.get(bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Закладка не найдена")
    return bookmark
