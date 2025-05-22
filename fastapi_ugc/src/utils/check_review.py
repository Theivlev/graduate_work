from src.crud.base import BaseMongoCRUD
from src.services.reviews import get_reviews_service

from fastapi import Depends, HTTPException


async def validate_review_exists(review_id: str, service: BaseMongoCRUD = Depends(get_reviews_service)):
    review = await service.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Рецензия не найдена")
    return review
