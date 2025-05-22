from typing import List, Tuple
from uuid import UUID

from pymongo.errors import DuplicateKeyError
from src.crud.base import BaseMongoCRUD
from src.models.review import UserReviews
from src.paginations.pagination import PaginationLimits
from src.services.reviews import get_reviews_service
from src.shemas.user_reviews import UserReviewCreateDTO, UserReviewResponse
from src.utils.check_review import validate_review_exists
from src.auth_server.schemas.models import TokenValidationResult    
from src.auth_server.security import require_valid_token
from src.utils.security import ensure_user_owns_resource

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Security

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserReviewResponse],
    summary="Получение списка рецензий",
    description="Возвращает список рецензий",
)
async def get_reviews_films(
    user_id: str,
    pagination: Tuple[int, int] = Depends(PaginationLimits.get_pagination_params),
    service: BaseMongoCRUD = Depends(get_reviews_service),
):
    """
    Получить список рецензий.
    """
    try:
        uuid_obj = UUID(user_id)

        page_number, page_size = pagination
        filter_ = {"user_id": uuid_obj}

        reviews = await service.find(filter_, page_number, page_size)

        return [UserReviewResponse.from_review(review) for review in reviews]

    except HTTPException as e:
        raise e
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный формат user_id. Ожидается UUID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.get(
    "/{review_id}",
    response_model=UserReviewResponse,
    summary="Получение рецензии",
    description="Возвращает рецензию",
)
async def get_review_films(
    review_id: str,
    service: BaseMongoCRUD = Depends(get_reviews_service),
):
    """
    Получить рецензию.
    """
    try:
        review = await service.get(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Рецензия не найдена")

        return UserReviewResponse.from_review(review)

    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Некорректный формат review_id: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.post(
    "/",
    response_model=None,
    summary="Добавление рецензии",
    description="Добавляет рецензию",
)
async def add_reviews_films(
    review_data: UserReviewCreateDTO,
    service: BaseMongoCRUD = Depends(get_reviews_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    """
    Добавить рецензию.
    """
    ensure_user_owns_resource(review_data.user_id, token_payload.user_id, "добавить рецензию")

    try:
        new_review = await service.create(review_data.model_dump(by_alias=True))
        return new_review

    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Рецензия уже существует")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Некорректные данные: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.delete(
    "/{review_id}",
    response_model=dict,
    summary="Удаление рецензии",
    description="Удаляет рецензию",
)
async def remove_review(
    review: UserReviews = Depends(validate_review_exists),
    service: BaseMongoCRUD = Depends(get_reviews_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    """
    Удалить рецензию.
    """
    ensure_user_owns_resource(review.user_id, token_payload.user_id, "удалить рецензию")
    
    try:
        success = await service.delete(str(review.id))
        if not success:
            raise HTTPException(status_code=404, detail="Рецензия не найдена")
        return {"message": "Рецензия успешно удалена"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.put(
    "/{review_id}",
    response_model=dict,
    summary="Обновление рецензии",
    description="Обновляет рецензию",
)
async def update_review(
    review_text: str,
    review: UserReviews = Depends(validate_review_exists),
    service: BaseMongoCRUD = Depends(get_reviews_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    """
    Обновить рецензию.
    """
    ensure_user_owns_resource(review.user_id, token_payload.user_id, "обновить рецензию")

    try:
        if not review_text.strip():
            raise HTTPException(status_code=400, detail="Текст рецензии не может быть пустым")

        data = {"review_text": review_text}
        success = await service.update(str(review.id), data)
        if not success:
            raise HTTPException(status_code=404, detail="Рецензия не найдена")
        return {"message": "Рецензия успешно обновлена"}

    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Некорректные данные: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
