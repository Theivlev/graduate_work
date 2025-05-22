from typing import Annotated

from fastapi_cache.decorator import cache
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.auth_server.schemas.models import TokenValidationResult
from src.auth_server.security import require_valid_token
from src.models.film import MovieBaseDTO, MovieInfoDTO
from src.services.film_service import FilmService, get_film_service

from fastapi import APIRouter, Depends, Path, Query, Request, Response, Security

router = APIRouter()
tracer = trace.get_tracer(__name__)


@router.get(
    "/",
    response_model=list[MovieBaseDTO],
    summary="Get films",
    description="Get films with genre, sort and pagination.",
)
@cache(expire=60)
async def get_films(
    request: Request,
    response: Response,
    genre: Annotated[
        str | None,
        Query(
            title="genre name",
            description="Genre name for the items to search in the database",
        ),
    ] = None,
    page_size: Annotated[
        int,
        Query(
            title="page size",
            description="Page size for count of items to response",
            gt=0,
        ),
    ] = 50,
    page_number: Annotated[
        int,
        Query(
            title="page number",
            description="Page number for count of items to response",
            gt=0,
        ),
    ] = 1,
    sort: Annotated[
        str,
        Query(
            title="name for sort",
            description="To sort by rating",
        ),
    ] = "imdb_rating",
    film_service: FilmService = Depends(get_film_service),
) -> list[MovieBaseDTO]:
    with tracer.start_as_current_span(
        "api.get_films",
        kind=SpanKind.SERVER,
        attributes={
            "genre": genre,
            "page_size": page_size,
            "page_number": page_number,
            "sort": sort,
            "http.request_id": request.headers.get("X-Request-Id"),
        },
    ) as span:
        try:
            films = await film_service.search(genre=genre, page_number=page_number, page_size=page_size, sort=sort)
            span.set_attribute("films_count", len(films))
            return films
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.get(
    "/{film_id}",
    response_model=MovieInfoDTO,
    summary="Get film",
    description="Get film details with all parameters of model Movie.",
)
@cache(expire=60)
async def film_details(
    request: Request,
    response: Response,
    film_id: Annotated[
        str,
        Path(
            title="film id",
            description="Film id for the item to search in the database",
        ),
    ],
    film_service: FilmService = Depends(get_film_service),
    token_payload: TokenValidationResult = Security(require_valid_token),
) -> MovieInfoDTO:
    with tracer.start_as_current_span(
        "api.film_details",
        kind=SpanKind.SERVER,
        attributes={"film_id": film_id, "http.request_id": request.headers.get("X-Request-Id")},
    ) as span:
        try:
            film = await film_service.get_by_id(film_id)
            span.set_attribute("film_found", True)
            return film
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.get(
    "/search/",
    response_model=list[MovieBaseDTO],
    summary="Get films from search",
    description="Get films from search with sort and pagination.",
)
@cache(expire=60)
async def search_films(
    request: Request,
    response: Response,
    page_size: Annotated[
        int,
        Query(
            title="page size",
            description="Page size for count of items to response",
            gt=0,
        ),
    ] = 50,
    page_number: Annotated[
        int,
        Query(
            title="page number",
            description="Page number for count of items to response",
            gt=0,
        ),
    ] = 1,
    query: Annotated[
        str,
        Query(
            title="search words",
            description="Words for search of items in the database",
        ),
    ] = None,
    film_service: FilmService = Depends(get_film_service),
) -> list[MovieBaseDTO]:
    with tracer.start_as_current_span(
        "api.search_films",
        kind=SpanKind.SERVER,
        attributes={
            "page_size": page_size,
            "page_number": page_number,
            "query": query,
            "http.request_id": request.headers.get("X-Request-Id"),
        },
    ) as span:
        try:
            films = await film_service.search(
                page_number=page_number,
                page_size=page_size,
                title=query,
            )
            span.set_attribute("films_count", len(films))
            return films
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise
