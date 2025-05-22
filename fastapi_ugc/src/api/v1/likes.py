from typing import List, Tuple
from uuid import UUID

from pymongo.errors import DuplicateKeyError
from src.crud.base import BaseMongoCRUD
from src.models.like import UserLikes
from src.paginations.pagination import PaginationLimits
from src.services.likes import get_likes_service
from src.shemas.user_likes import UserLikeCreateDTO, UserLikeResponse
from src.utils.check_like import validate_like_exists
from src.auth_server.schemas.models import TokenValidationResult
from src.auth_server.security import require_valid_token
from src.utils.security import ensure_user_owns_resource


from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.params import Security

router = APIRouter()

@router.get(
    "/",
    response_model=List[UserLikeResponse],
    summary="Получение списка лайков",
    description="Возвращает список лайков",
)
async def get_likes_films(
    user_id: str,
    pagination: Tuple[int, int] = Depends(PaginationLimits.get_pagination_params),
    service: BaseMongoCRUD = Depends(get_likes_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    """
    Получить список лайков.
    """
    try:
        uuid_obj = UUID(user_id)
        page_number, page_size = pagination

        filter_ = {"user_id": uuid_obj}
        likes = await service.find(filter_, page_number, page_size)

        return [UserLikeResponse.from_user_like(like) for like in likes]
    except HTTPException as e:
        raise e
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный формат user_id. Ожидается UUID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.get(
    "/{like_id}",
    response_model=UserLikeResponse,
    summary="Получение лайка",
    description="Возвращает лайк",
)
async def get_like_films(
    like_id: str,
    service: BaseMongoCRUD = Depends(get_likes_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    """
    Получить лайк.
    """
    try:
        like = await service.get(like_id)
        if not like:
            raise HTTPException(status_code=404, detail="Лайк не найден")

        return UserLikeResponse.from_user_like(like)

    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Некорректный формат like_id: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.post(
    "/",
    response_model=None,
    summary="Добавление лайка",
    description="Добавляет лайк"
)
async def add_likes_films(
    like_data: UserLikeCreateDTO,
    service: BaseMongoCRUD = Depends(get_likes_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    """
    Добавить лайк.
    """
    #ensure_user_owns_resource(like_data.user_id, token_payload.user_id, "добавить лайк")

    try:
        new_like = await service.create(like_data.model_dump(by_alias=True))
        return new_like

    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Лайк уже существует")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Некорректные данные: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.delete(
    "/{like_id}",
    response_model=dict,
    summary="Удаление лайка",
    description="Удаляет лайк",
)
async def remove_like(
    like: UserLikes = Depends(validate_like_exists),
    service: BaseMongoCRUD = Depends(get_likes_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    """
    Удалить лайк.
    """
    ensure_user_owns_resource(like.user_id, token_payload.user_id, "Вы не можете удалить лайк другого пользователя")

    try:
        success = await service.delete(str(like.id))
        if not success:
            raise HTTPException(status_code=404, detail="Лайк не найден")
        return {"message": "Лайк успешно удален"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.put(
    "/{like_id}",
    response_model=dict,
    summary="Обновление лайка",
    description="Обновляет лайк",
)
async def update_like(
    rating: int = Query(ge=1, le=10, description="Оценка рейтинга"),
    like: UserLikes = Depends(validate_like_exists),
    service: BaseMongoCRUD = Depends(get_likes_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
):
    ensure_user_owns_resource(like.user_id, token_payload.user_id, "обновить лайк")
    
    try:
        data = {"rating": rating}
        success = await service.update(str(like.id), data)
        if not success:
            raise HTTPException(status_code=404, detail="Лайк не найден")
        return {"message": "Лайк успешно обновлен"}
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Некорректные данные: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
