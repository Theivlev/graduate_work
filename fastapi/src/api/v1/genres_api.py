from typing import Annotated, List

from fastapi_cache.decorator import cache
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.models.genre import GenreDTO
from src.services.genre_service import GenreService, get_genre_service

from fastapi import APIRouter, Depends, Path, Query, Request, Response

router = APIRouter()
tracer = trace.get_tracer(__name__)


@router.get(
    "/",
    response_model=List[GenreDTO],
    summary="Get genres",
    description="Get all genres.",
)
@cache(expire=60)
async def get_genres(
    request: Request,
    response: Response,
    genre_service: GenreService = Depends(get_genre_service),
    page_number: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1),
) -> List[GenreDTO]:
    with tracer.start_as_current_span(
        "api.get_genres",
        kind=SpanKind.SERVER,
        attributes={
            "page_number": page_number,
            "page_size": page_size,
            "http.request_id": request.headers.get("X-Request-Id"),
        },
    ) as span:
        try:
            genres = await genre_service.search(page_number=page_number, page_size=page_size)
            span.set_attribute("genres_count", len(genres))
            return genres
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.get(
    "/{genre_id}",
    response_model=GenreDTO,
    summary="Get genre",
    description="Get genre details.",
)
@cache(expire=60)
async def genre_details(
    request: Request,
    response: Response,
    genre_id: Annotated[
        str,
        Path(
            title="genre id",
            description="Genre id for the item to search in the database",
        ),
    ],
    genre_service: GenreService = Depends(get_genre_service),
) -> GenreDTO:
    with tracer.start_as_current_span(
        "api.genre_details",
        kind=SpanKind.SERVER,
        attributes={"genre_id": genre_id, "http.request_id": request.headers.get("X-Request-Id")},
    ) as span:
        try:
            genre = await genre_service.get_by_id(genre_id)
            span.set_attribute("genre_found", True)
            return genre
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise
