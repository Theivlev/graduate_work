from typing import Annotated

from fastapi_cache.decorator import cache
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.models.film import MovieBaseDTO
from src.models.person import PersonInfoDTO
from src.services.film_service import FilmService, get_film_service
from src.services.person_service import PersonService, get_person_service

from fastapi import APIRouter, Depends, Path, Query, Request, Response

router = APIRouter()
tracer = trace.get_tracer(__name__)


@router.get(
    "/{person_id}",
    response_model=PersonInfoDTO,
    summary="Get person",
    description="Get person deatails.",
)
@cache(expire=60)
async def person_details(
    person_id: Annotated[
        str,
        Path(
            title="person id",
            description="Person id for the item to search in the database",
        ),
    ],
    request: Request,
    response: Response,
    person_service: PersonService = Depends(get_person_service),
) -> PersonInfoDTO:
    with tracer.start_as_current_span(
        "api.person_details",
        kind=SpanKind.SERVER,
        attributes={"person_id": person_id, "http.request_id": request.headers.get("X-Request-Id")},
    ) as span:
        try:
            person = await person_service.get_by_id(person_id)
            span.set_attribute("person_found", True)
            return person
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.get(
    "/search/",
    response_model=list[PersonInfoDTO],
    summary="Get persons from search",
    description="Get persons from search with sort and pagination.",
)
@cache(expire=60)
async def search_person(
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
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonInfoDTO]:
    with tracer.start_as_current_span(
        "api.search_person",
        kind=SpanKind.SERVER,
        attributes={
            "page_size": page_size,
            "page_number": page_number,
            "query": query,
            "http.request_id": request.headers.get("X-Request-Id"),
        },
    ) as span:
        try:
            persons = await person_service.search(
                page_number=page_number,
                page_size=page_size,
                full_name=query,
            )
            span.set_attribute("persons_count", len(persons))
            return persons
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.get(
    "/{person_id}/film",
    response_model=list[MovieBaseDTO],
    summary="Get films of person",
    description="Get films of person with parameters of model Movie.",
)
@cache(expire=60)
async def get_films(
    request: Request,
    response: Response,
    person_id: Annotated[
        str,
        Path(
            title="person id",
            description="Person id for the films to search in the database",
        ),
    ],
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
) -> list[MovieBaseDTO]:
    with tracer.start_as_current_span(
        "api.get_films",
        kind=SpanKind.SERVER,
        attributes={"person_id": person_id, "http.request_id": request.headers.get("X-Request-Id")},
    ) as span:
        try:
            person = await person_service.get_by_id(person_id)
            films = [await film_service.get_by_id(film.id) for film in person.films]
            span.set_attribute("films_count", len(films))
            return films
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise
